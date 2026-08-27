"""FastAPI endpoints for player profile, character creation, and loadouts."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from server.database import get_db
from server.auth.dependencies import get_current_user
from server.player.player_service import player_service
from shared.models.db_models import User
from shared.schemas.player_schemas import CharacterCreateRequest, PlayerProfile, PlayerStats, LoadoutConfig

router = APIRouter(prefix="/api/v1/player", tags=["Player & Character"])


@router.get("/profile", response_model=PlayerProfile)
async def get_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Fetches the authenticated player's full profile, stats, and active loadout."""
    try:
        return await player_service.get_player_profile(session, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/character", status_code=status.HTTP_201_CREATED)
async def create_character(
    req: CharacterCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Creates a new tactical character class for the player."""
    char = await player_service.create_character(session, current_user.id, req)
    return {
        "character_id": char.id,
        "name": char.name,
        "class": char.character_class,
        "faction": char.faction,
    }
