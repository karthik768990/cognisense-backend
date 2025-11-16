"""
Tracking API Endpoints
Receives activity and engagement data from browser extension and stores for analysis.
Phase 1: in-memory store (replace with DB in future)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from time import time
from loguru import logger
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta

from app.ml.sentiment_analyzer import SentimentAnalyzer
from app.ml.zero_shot_classifier import ZeroShotClassifier
from app.ml.emotion_detector import EmotionDetector
from app.core.supabase_client import supabase
from app.api.v1.content import analyze_content as analyze_content_route
from app.scraper.scraper import extract_visible_text_and_metadata

router = APIRouter()

# Simple in-memory activity store: {user_id: [activities...]}
ACTIVITY_STORE: dict[str, list[dict]] = {}

# ML services (lightweight per-process instances)
sentiment_analyzer = SentimentAnalyzer()
zero_shot = ZeroShotClassifier()
emotion_detector = EmotionDetector()


class ActivityIn(BaseModel):
    user_id: str = Field(..., description="User identifier")
    url: str = Field(..., description="URL of the active tab")
    title: Optional[str]
    text: Optional[str] = Field(None, description="Visible text scraped from page")
    start_ts: Optional[float] = None
    end_ts: Optional[float] = None
    duration_seconds: Optional[float] = None
    clicks: int = 0
    keypresses: int = 0
    engagement_score: Optional[float] = None


@router.post("/ingest")
async def ingest_activity(payload: ActivityIn):
    """Receive activity data from browser extension.

    Performs optional lightweight analysis for quick dashboard insights and stores the record.
    """
    if not payload.user_id or not payload.url:
        raise HTTPException(status_code=400, detail="user_id and url required")

    now = time()
    record = payload.dict()
    record.setdefault("received_at", now)

    # Basic duration inference
    if not record.get("duration_seconds") and record.get("start_ts") and record.get("end_ts"):
        try:
            record["duration_seconds"] = float(record["end_ts"]) - float(record["start_ts"])
        except Exception:
            record["duration_seconds"] = None

    # Determine domain and any user-configured category override
    parsed = urlparse(record["url"]) if record.get("url") else None
    domain = (parsed.netloc or "").lower() if parsed else None
    override_category: Optional[str] = None
    try:
        if supabase is not None and record.get("user_id") and domain:
            rules_resp = supabase.table("user_domain_categories").select("domain_pattern,category,priority").eq("user_id", record["user_id"]).execute()
            rules = getattr(rules_resp, "data", []) or []

            def pattern_matches(d: str, pat: str) -> bool:
                p = (pat or "").lower().strip()
                p = p.replace("http://", "").replace("https://", "")
                p = p.lstrip("*.")
                if not p:
                    return False
                return d == p or d.endswith("." + p) or d.endswith(p)

            matches = [r for r in rules if pattern_matches(domain, r.get("domain_pattern", ""))]
            if matches:
                # Highest priority first, then longest pattern wins
                matches.sort(key=lambda r: (-(r.get("priority") or 1), -len((r.get("domain_pattern") or ""))))
                override_category = matches[0].get("category")
    except Exception as e:
        logger.debug(f"Failed to resolve category override: {e}")

    # Fetch page content (if text not already provided) using the scraper service
    page_text: Optional[str] = record.get("text")
    if not page_text:
        try:
            scraped = extract_visible_text_and_metadata(record["url"]) or {}
            page_text = scraped.get("visible_text")
            if not record.get("title") and scraped.get("title"):
                record["title"] = scraped.get("title")
            record["text"] = page_text
        except Exception as e:
            logger.debug(f"Scrape failed for url={record['url']}: {e}")
            page_text = None

    # Run unified analysis via the content analyzer route function
    analysis_result = None
    if page_text and isinstance(page_text, str) and page_text.strip():
        try:
            analysis_result = await analyze_content_route(
                text=page_text,
                url=record.get("url"),
                analyze_sentiment=True,
                analyze_category=False if override_category else True,
                analyze_emotions=True,
            )
            # Attach key fields back into the record for immediate use/echo
            if isinstance(analysis_result, dict):
                if "sentiment" in analysis_result:
                    record["sentiment"] = analysis_result["sentiment"]
                if override_category:
                    record["classified_category"] = override_category
                elif "category" in analysis_result:
                    record["classified_category"] = analysis_result["category"].get("primary")
                    record["classified_scores"] = analysis_result["category"].get("all_categories", [])
                if "emotions" in analysis_result:
                    record["emotions"] = analysis_result["emotions"].get("all_emotions")
        except HTTPException as he:
            # If the analyzer raises HTTPException, log and proceed with local lightweight analysis as fallback
            logger.debug(f"Route analyzer failed: {he}")
            analysis_result = None
        except Exception as e:
            logger.debug(f"Unexpected analysis error: {e}")
            analysis_result = None

    # Fallback: quick local analysis if unified analyzer was unavailable
    if not analysis_result and record.get("text"):
        try:
            sentiment = sentiment_analyzer.analyze(record["text"])
            record["sentiment"] = sentiment
        except Exception as e:
            logger.debug(f"Sentiment analysis failed: {e}")

        if override_category:
            record["classified_category"] = override_category
        else:
            try:
                cat = zero_shot.classify_with_group(record["text"])
                if not cat.get("error"):
                    record["classified_category"] = cat.get("labels", [None])[0]
                    record["category_group"] = cat.get("category_group")
                    record["classified_scores"] = cat.get("scores", [])
            except Exception as e:
                logger.debug(f"Category classification failed: {e}")

        try:
            emotions = emotion_detector.detect(record["text"])
            record["emotions"] = emotions
        except Exception as e:
            logger.debug(f"Emotion detection failed: {e}")

    # Store
    ACTIVITY_STORE.setdefault(payload.user_id, []).append(record)
    logger.info(f"Ingested activity for user={payload.user_id} url={payload.url}")
    
    # Persist to database via Supabase if configured
    _persist_errors: List[str] = []
    try:
        await _persist_to_database(record, analysis_result)
    except Exception as e:
        logger.warning(f"DB persistence failed: {e}")
        _persist_errors.append(str(e))

    response = {"status": "ok", "ingested": 1}
    if _persist_errors:
        response["warnings"] = {"database": _persist_errors}
    return response


@router.get("/activity/{user_id}")
async def get_activity(user_id: str, limit: int = Query(100, ge=1, le=1000)):
    """Fetch recent activity records for a user (in-memory)."""
    items = ACTIVITY_STORE.get(user_id, [])
    # return last `limit` items
    return {"user_id": user_id, "count": len(items), "items": items[-limit:]}


@router.delete("/activity/{user_id}")
async def delete_activity(user_id: str):
    """Clear activity for a user (useful in dev/testing)."""
    removed = ACTIVITY_STORE.pop(user_id, None)
    return {"status": "ok", "removed": 0 if removed is None else len(removed)}


async def _persist_to_database(record: dict, analysis_result: Optional[dict]):
    """Persist session and analysis results into Supabase tables.

    Tables: page_view_sessions, content_analysis
    """
    if supabase is None:
        raise RuntimeError("Supabase client not configured")

    user_id = record.get("user_id")
    url = record.get("url")
    parsed = urlparse(url) if url else None
    domain = (parsed.netloc or "").lower() if parsed else None

    # Build start/end times
    now_dt = datetime.now(timezone.utc)
    start_ts = record.get("start_ts")
    end_ts = record.get("end_ts")
    duration = record.get("duration_seconds")

    def _to_dt(ts: Optional[float]) -> Optional[datetime]:
        if ts is None:
            return None
        try:
            return datetime.fromtimestamp(float(ts), tz=timezone.utc)
        except Exception:
            return None

    start_dt = _to_dt(start_ts)
    end_dt = _to_dt(end_ts)
    if not start_dt and end_dt and duration:
        try:
            start_dt = end_dt - timedelta(seconds=float(duration))
        except Exception:
            start_dt = None
    if not end_dt and start_dt and duration:
        try:
            end_dt = start_dt + timedelta(seconds=float(duration))
        except Exception:
            end_dt = None
    if not start_dt and not end_dt:
        # Fallback to now for both
        start_dt = now_dt
        end_dt = now_dt

    # Insert session row
    try:
        session_payload = {
            "user_id": user_id,
            "url": url,
            "domain": domain,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
        }
        supabase.table("page_view_sessions").insert(session_payload).execute()
    except Exception as e:
        logger.warning(f"Failed to insert page_view_sessions: {e}")

    # Prepare content_analysis upsert if analysis available
    if (analysis_result and isinstance(analysis_result, dict)) or record.get("classified_category"):
        try:
            emotions = ((analysis_result or {}).get("emotions") or {}).get("all_emotions") or []
            # index by label
            emo_map = {str(e.get("label")).lower(): float(e.get("score", 0.0)) for e in emotions if isinstance(e, dict)}
            dom = ((analysis_result or {}).get("emotions") or {}).get("dominant") or {}
            dominant_label = dom.get("label") if isinstance(dom, dict) else None
            category_primary = ((analysis_result or {}).get("category") or {}).get("primary") or record.get("classified_category")

            analysis_payload = {
                "user_id": user_id,
                "page_url": url,
                "happy_score": emo_map.get("joy", 0.0),
                "sad_score": emo_map.get("sadness", 0.0),
                "angry_score": emo_map.get("anger", 0.0),
                "neutral_score": emo_map.get("neutral", 0.0),
                "dominant_emotion": dominant_label,
                "system_suggested_category": category_primary,
            }
            # Upsert on page_url uniqueness
            supabase.table("content_analysis").upsert(analysis_payload, on_conflict="page_url").execute()
        except Exception as e:
            logger.warning(f"Failed to upsert content_analysis: {e}")

