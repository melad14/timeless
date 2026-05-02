"""API routes module"""

from fastapi import APIRouter
from app.api.routes import auth, users, time_capsules

api_router = APIRouter(prefix="/api/v1")

# Include routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(time_capsules.router)

__all__ = ["api_router"]
