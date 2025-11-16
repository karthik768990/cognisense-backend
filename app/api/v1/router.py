"""
API v1 Main Router
Aggregates all v1 endpoint routers
"""

from fastapi import APIRouter
from loguru import logger

# Import routers
from app.api.v1 import content
from app.api.v1.dashboard.dashboard import router as dashboard_router
from app.api.v1.dashboard.insights import router as insights_router
from app.api.v1.dashboard.settings import router as settings_router
#from app.api.v1 import tracking, categories, dashboard

# Optional auth import
try:
    from app.api.v1.auth import auth
    AUTH_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Auth module disabled due to missing dependencies: {e}")
    AUTH_AVAILABLE = False
# from app.api.v1 import tracking, categories, dashboard  # TODO: Create these
api_router = APIRouter()

# Include sub-routers
api_router.include_router(content.router, prefix="/content", tags=["Content Analysis"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(insights_router, prefix="/dashboard/insights", tags=["Dashboard Insights"])
api_router.include_router(settings_router, prefix="/dashboard/settings", tags=["Dashboard Settings"])
# api_router.include_router(tracking.router, prefix="/tracking", tags=["Tracking"])
# api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])

# Include auth router if available
if AUTH_AVAILABLE:
    api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(tracking.router, prefix="/tracking", tags=["Tracking"])  # TODO
# api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])  # TODO
# api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])  # TODO


@api_router.get("/ping")
async def ping():
    """Simple API health check"""
    return {"message": "pong", "api_version": "v1"}
