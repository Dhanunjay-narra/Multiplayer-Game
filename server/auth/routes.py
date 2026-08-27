"""FastAPI endpoints for authentication and user accounts."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from server.database import get_db
from server.auth.auth_service import auth_service
from server.auth.dependencies import get_current_user
from shared.schemas.auth_schemas import RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest
from shared.models.db_models import User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, session: AsyncSession = Depends(get_db)):
    """Registers a new player account and creates initial profile and wallet."""
    try:
        user = await auth_service.register_user(session, req)
        # Auto-login after registration
        return await auth_service.authenticate_user(
            session, LoginRequest(username_or_email=req.username, password=req.password)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, session: AsyncSession = Depends(get_db)):
    """Authenticates credentials and returns JWT access and refresh tokens."""
    try:
        return await auth_service.authenticate_user(session, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshTokenRequest, session: AsyncSession = Depends(get_db)):
    """Generates a new access token using a valid refresh token."""
    try:
        return await auth_service.refresh_access_token(session, req.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/me")
async def get_my_info(current_user: User = Depends(get_current_user)):
    """Returns basic account details for the authenticated user."""
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at,
    }
