"""FastAPI endpoints for matchmaking queues and ticket polling."""
from fastapi import APIRouter, Depends, HTTPException, status
from server.auth.dependencies import get_current_user
from server.matchmaking.matchmaker import matchmaker
from server.matchmaking.server_allocator import server_allocator
from shared.models.db_models import User
from shared.schemas.matchmaking_schemas import MatchmakingTicket, MatchReservation

router = APIRouter(prefix="/api/v1/matchmaking", tags=["Matchmaking"])


@router.post("/queue", response_model=MatchmakingTicket)
async def enter_queue(
    region: str = "us-east",
    current_user: User = Depends(get_current_user),
):
    """Enqueues the player for skill-based matchmaking."""
    return matchmaker.enqueue_player(
        player_id=current_user.id,
        username=current_user.username,
        region=region,
    )


@router.get("/ticket/{ticket_id}", response_model=MatchmakingTicket)
async def get_ticket(ticket_id: str, current_user: User = Depends(get_current_user)):
    """Checks the matchmaking ticket status."""
    ticket = matchmaker.get_ticket_status(ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.get("/reservation/{match_id}", response_model=MatchReservation)
async def get_reservation(match_id: str, current_user: User = Depends(get_current_user)):
    """Retrieves server address and access token for an assigned match."""
    reservation = server_allocator.get_reservation(match_id)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return reservation


@router.post("/cancel")
async def cancel_queue(current_user: User = Depends(get_current_user)):
    """Leaves the matchmaking queue."""
    ticket_id = matchmaker.dequeue_player(current_user.id)
    return {"message": "Left queue", "ticket_id": ticket_id}
