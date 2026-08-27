"""Authentication service managing account creation, authentication, and sessions."""
import uuid
import time
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.db_models import User, PlayerProfileModel, PlayerStatsModel, WalletModel, InventoryModel
from shared.schemas.auth_schemas import RegisterRequest, LoginRequest, TokenResponse, SessionInfo
from shared.enums.game_enums import AccountRole
from server.auth.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token


class AuthService:
    """Business logic for user authentication, registration, and sessions."""

    async def register_user(self, session: AsyncSession, req: RegisterRequest) -> User:
        """Registers a new user and sets up their initial player profile, wallet, and inventory."""
        # Check existing username
        stmt = select(User).where((User.username == req.username) | (User.email == req.email))
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("Username or email already in use")

        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        role_str = req.role.value if hasattr(req.role, "value") else str(req.role)
        user = User(
            id=user_id,
            username=req.username,
            email=req.email,
            password_hash=hash_password(req.password),
            role=role_str,
            is_active=True,
            is_banned=False,
            created_at=time.time(),
            updated_at=time.time(),
        )
        session.add(user)

        # Initialize profile & stats
        profile = PlayerProfileModel(
            id=f"prof_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            level=1,
            current_xp=0,
            rank_tier="UNRANKED",
            rank_points=0,
            mmr=1200,
            active_faction="SOLARIS_HEGEMONY",
        )
        session.add(profile)

        stats = PlayerStatsModel(
            id=f"stat_{uuid.uuid4().hex[:12]}",
            profile_id=profile.id,
        )
        session.add(stats)

        # Initialize wallet & inventory
        wallet = WalletModel(
            id=f"wal_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            credits=1000.0,
            energy_cells=100.0,
            alloy_materials=50.0,
        )
        session.add(wallet)

        inventory = InventoryModel(
            id=f"inv_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            max_slots=24,
        )
        session.add(inventory)

        await session.commit()
        return user

    async def authenticate_user(self, session: AsyncSession, req: LoginRequest) -> TokenResponse:
        """Validates credentials and generates access/refresh tokens."""
        stmt = select(User).where((User.username == req.username_or_email) | (User.email == req.username_or_email))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(req.password, user.password_hash):
            raise ValueError("Invalid username or password")

        if user.is_banned:
            raise PermissionError("Account is banned from Nexus Frontier")

        if not user.is_active:
            raise PermissionError("Account is inactive or suspended")

        access_token = create_access_token(user.id, user.username, AccountRole(user.role))
        refresh_token = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            username=user.username,
            role=AccountRole(user.role),
        )

    async def refresh_access_token(self, session: AsyncSession, refresh_token: str) -> TokenResponse:
        """Exchanges a valid refresh token for a new access token."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid or expired refresh token")

        user_id = payload.get("sub")
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or user.is_banned:
            raise PermissionError("User invalid or banned")

        access_token = create_access_token(user.id, user.username, AccountRole(user.role))
        new_refresh = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            user_id=user.id,
            username=user.username,
            role=AccountRole(user.role),
        )


auth_service = AuthService()
