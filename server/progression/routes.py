"""FastAPI endpoints for season battle pass and progression."""
from fastapi import APIRouter, Depends
from server.auth.dependencies import get_current_user
from server.progression.progression_service import progression_service, SeasonPassTrack
from shared.models.db_models import User

router = APIRouter(prefix="/api/v1/progression", tags=["Progression & Battle Pass"])


@router.get("/season-pass", response_model=SeasonPassTrack)
async def get_season_pass(current_user: User = Depends(get_current_user)):
    """Returns player's current Battle Pass tier and XP progress."""
    return progression_service.get_or_create_pass(current_user.id)
