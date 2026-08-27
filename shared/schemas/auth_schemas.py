"""Authentication and account session schemas."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from shared.enums.game_enums import AccountRole


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=24)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=64)
    role: AccountRole = AccountRole.PLAYER


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user_id: str
    username: str
    role: AccountRole


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class SessionInfo(BaseModel):
    user_id: str
    username: str
    role: AccountRole
    session_id: str
    created_at: float
