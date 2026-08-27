"""FastAPI endpoints for lobbies and parties."""
from fastapi import APIRouter, Depends, HTTPException, status
from server.auth.dependencies import get_current_user
from server.lobby.lobby_service import lobby_service
from shared.models.db_models import User
from shared.schemas.lobby_schemas import LobbyCreateRequest, LobbyJoinRequest, LobbyState

router = APIRouter(prefix="/api/v1/lobby", tags=["Lobby & Parties"])


@router.post("/create", response_model=LobbyState, status_code=status.HTTP_201_CREATED)
async def create_lobby(req: LobbyCreateRequest, current_user: User = Depends(get_current_user)):
    """Creates a new game lobby."""
    return lobby_service.create_lobby(current_user.id, current_user.username, req)


@router.post("/join", response_model=LobbyState)
async def join_lobby(req: LobbyJoinRequest, current_user: User = Depends(get_current_user)):
    """Joins an existing lobby."""
    try:
        return lobby_service.join_lobby(req.lobby_id, current_user.id, current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/leave")
async def leave_lobby(current_user: User = Depends(get_current_user)):
    """Leaves the current lobby."""
    lobby_id = lobby_service.leave_lobby(current_user.id)
    return {"message": "Left lobby", "lobby_id": lobby_id}


@router.post("/ready")
async def toggle_ready(current_user: User = Depends(get_current_user)):
    """Toggles ready status in lobby."""
    try:
        is_ready = lobby_service.toggle_ready(current_user.id)
        return {"is_ready": is_ready}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/current", response_model=LobbyState)
async def get_my_lobby(current_user: User = Depends(get_current_user)):
    """Returns details for player's current lobby."""
    lobby = lobby_service.get_player_lobby(current_user.id)
    if not lobby:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not currently in a lobby")
    return lobby
