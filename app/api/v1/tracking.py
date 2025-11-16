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

from app.ml.sentiment_analyzer import SentimentAnalyzer
from app.ml.zero_shot_classifier import ZeroShotClassifier
from app.ml.emotion_detector import EmotionDetector

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
    category_override: Optional[str] = None


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

    # Quick analysis if text provided
    if record.get("text"):
        try:
            sentiment = sentiment_analyzer.analyze(record["text"])
            record["sentiment"] = sentiment
        except Exception as e:
            logger.debug(f"Sentiment analysis failed: {e}")

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
    return {"status": "ok", "ingested": 1}


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
