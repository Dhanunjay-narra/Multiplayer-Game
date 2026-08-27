"""Cryptographic utilities, password hashing, and JWT token management."""
import hashlib
import hmac
import os
import time
from typing import Any, Dict, Optional
import jwt
from shared.enums.game_enums import AccountRole

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "nexus-frontier-dev-secret-key-982374982374")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600 * 4      # 4 hours
REFRESH_TOKEN_EXPIRE_SECONDS = 86400 * 14    # 14 days


def hash_password(password: str) -> str:
    """Hashes password with SHA256 + salt."""
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against the stored salt$hash."""
    try:
        salt, key_hex = hashed_password.split("$")
        computed_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return hmac.compare_digest(computed_key.hex(), key_hex)
    except Exception:
        return False


def create_access_token(user_id: str, username: str, role: AccountRole = AccountRole.PLAYER) -> str:
    """Creates a signed JWT access token."""
    now = time.time()
    role_str = role.value if hasattr(role, "value") else str(role)
    payload: Dict[str, Any] = {
        "sub": user_id,
        "username": username,
        "role": role_str,
        "iat": now,
        "exp": now + ACCESS_TOKEN_EXPIRE_SECONDS,
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Creates a signed JWT refresh token."""
    now = time.time()
    payload: Dict[str, Any] = {
        "sub": user_id,
        "iat": now,
        "exp": now + REFRESH_TOKEN_EXPIRE_SECONDS,
        "type": "refresh",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
