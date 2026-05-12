"""API routes module"""

from fastapi import APIRouter
from app.api.routes import auth, users, time_capsules, messages, conversations, shared_capsules, complaints, cron

api_router = APIRouter(prefix="/api/v1")

# Include routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(time_capsules.router)
api_router.include_router(messages.router)
api_router.include_router(conversations.router)
api_router.include_router(shared_capsules.router)
api_router.include_router(complaints.router)
api_router.include_router(cron.router, prefix="/cron", tags=["cron"])

__all__ = ["api_router"]
