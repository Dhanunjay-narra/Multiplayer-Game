"""Nexus Frontier Social Package."""
from server.social.social_service import social_service, SocialService
from server.social.routes import router as social_router

__all__ = ["social_service", "SocialService", "social_router"]
