"""
Dashboard API
Provides aggregated summaries and simple metrics for UI consumption.
This implementation uses in-memory activity store from `tracking` (Phase 1).
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Literal
from collections import defaultdict
from datetime import datetime, timedelta
from loguru import logger

from app.api.v1 import tracking

router = APIRouter()


def _within_period(ts: float, period: Literal["daily", "weekly"]) -> bool:
    """Check if timestamp (seconds) is within the requested period from now."""
    now = datetime.utcnow()
    dt = datetime.fromtimestamp(ts)
    if period == "daily":
        return dt >= (now - timedelta(days=1))
    return dt >= (now - timedelta(days=7))


@router.get("/summary/{user_id}")
async def summary(user_id: str, period: Literal["daily", "weekly"] = Query("weekly")):
    """Return aggregated summary for a user: total time per site, category proportions, sentiment mix."""
    items = tracking.ACTIVITY_STORE.get(user_id, [])
    if not items:
        return {"user_id": user_id, "period": period, "summary": {}}

    total_time = 0.0
    time_per_site = defaultdict(float)
    category_counts = defaultdict(float)
    sentiment_counts = defaultdict(int)
    counted = 0

    for rec in items:
        ts = rec.get("received_at") or rec.get("end_ts") or rec.get("start_ts")
        if ts is None:
            continue
        try:
            tsf = float(ts)
        except Exception:
            continue
        if not _within_period(tsf, period):
            continue

        counted += 1
        dur = rec.get("duration_seconds") or 0.0
        try:
            dur = float(dur)
        except Exception:
            dur = 0.0
        total_time += dur
        site = rec.get("url") or "unknown"
        time_per_site[site] += dur

        cat = rec.get("category_override") or rec.get("classified_category")
        if cat:
            category_counts[cat] += dur if dur > 0 else 1

        sent = None
        s = rec.get("sentiment")
        if isinstance(s, dict):
            sent = s.get("label") or s.get("sentiment")
        elif isinstance(s, str):
            sent = s
        if sent:
            sentiment_counts[sent] += 1

    # Build top sites list
    top_sites = sorted(time_per_site.items(), key=lambda x: x[1], reverse=True)[:20]

    # Category proportions
    total_cat = sum(category_counts.values()) or 1
    categories = [{"category": k, "value": v, "proportion": v / total_cat} for k, v in category_counts.items()]

    # Sentiment breakdown
    total_sent = sum(sentiment_counts.values()) or 1
    sentiments = [{"sentiment": k, "count": v, "proportion": v / total_sent} for k, v in sentiment_counts.items()]

    summary = {
        "period": period,
        "records_counted": counted,
        "total_time_seconds": total_time,
        "top_sites": [{"site": s, "time_seconds": t} for s, t in top_sites],
        "categories": categories,
        "sentiments": sentiments,
    }

    logger.info(f"Generated summary for {user_id} period={period}")
    return {"user_id": user_id, "summary": summary}


@router.get("/sites/{user_id}")
async def sites_table(user_id: str, limit: int = Query(100, ge=1, le=1000)):
    """Return table-like list of sites with aggregated time and category for UI table view."""
    items = tracking.ACTIVITY_STORE.get(user_id, [])
    agg = defaultdict(lambda: {"time": 0.0, "visits": 0, "category": None})

    for rec in items:
        site = rec.get("url") or "unknown"
        dur = rec.get("duration_seconds") or 0.0
        try:
            dur = float(dur)
        except Exception:
            dur = 0.0
        agg[site]["time"] += dur
        agg[site]["visits"] += 1
        if not agg[site]["category"]:
            agg[site]["category"] = rec.get("category_override") or rec.get("classified_category")

    rows = []
    for site, data in agg.items():
        rows.append({"site": site, "time_seconds": data["time"], "visits": data["visits"], "category": data["category"]})

    rows = sorted(rows, key=lambda r: r["time_seconds"], reverse=True)[:limit]
    return {"user_id": user_id, "sites": rows}
