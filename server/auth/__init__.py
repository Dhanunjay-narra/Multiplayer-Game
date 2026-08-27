"""Nexus Frontier Auth Package."""
from server.auth.auth_service import auth_service, AuthService
from server.auth.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from server.auth.dependencies import get_current_user, require_role
from server.auth.routes import router as auth_router

__all__ = [
    "auth_service",
    "AuthService",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "hash_password",
    "verify_password",
    "get_current_user",
    "require_role",
    "auth_router",
]
