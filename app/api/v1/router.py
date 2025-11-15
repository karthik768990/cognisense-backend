"""
API v1 Main Router
Aggregates all v1 endpoint routers
"""

from fastapi import APIRouter

# Import routers
from app.api.v1 import content
# from app.api.v1 import auth, tracking, categories, dashboard  # TODO: Create these

api_router = APIRouter()

# Include sub-routers
api_router.include_router(content.router, prefix="/content", tags=["Content Analysis"])
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])  # TODO
# api_router.include_router(tracking.router, prefix="/tracking", tags=["Tracking"])  # TODO
# api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])  # TODO
# api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])  # TODO


@api_router.get("/ping")
async def ping():
    """Simple API health check"""
    return {"message": "pong", "api_version": "v1"}
