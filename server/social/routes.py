"""FastAPI endpoints for social interactions, friends, clans, and chat."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from server.auth.dependencies import get_current_user
from server.social.social_service import social_service
from shared.models.db_models import User
from shared.schemas.social_schemas import FriendRecord, ClanData, ChatMessageData
from shared.enums.game_enums import FactionType

router = APIRouter(prefix="/api/v1/social", tags=["Social & Clans"])


@router.get("/friends", response_model=List[FriendRecord])
async def get_friends(current_user: User = Depends(get_current_user)):
    """Returns player's friends list."""
    return social_service.get_friends(current_user.id)


@router.post("/clans", response_model=ClanData, status_code=status.HTTP_201_CREATED)
async def create_clan(
    name: str,
    tag: str,
    faction: FactionType = FactionType.SOLARIS_HEGEMONY,
    current_user: User = Depends(get_current_user),
):
    """Creates a new player clan."""
    try:
        return social_service.create_clan(current_user.id, current_user.username, name, tag, faction)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/chat", response_model=ChatMessageData)
async def send_chat(channel: str, content: str, current_user: User = Depends(get_current_user)):
    """Sends a chat message to a channel."""
    return social_service.send_chat_message(current_user.id, current_user.username, channel, content)
