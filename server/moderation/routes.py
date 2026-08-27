"""FastAPI endpoints for reports and moderation."""
from fastapi import APIRouter, Depends, HTTPException, status
from server.auth.dependencies import get_current_user, require_role
from server.moderation.moderation_service import moderation_service
from shared.models.db_models import User
from shared.schemas.admin_schemas import PlayerReportRequest, BanPlayerRequest
from shared.enums.game_enums import AccountRole

router = APIRouter(prefix="/api/v1/moderation", tags=["Moderation & Safety"])


@router.post("/report")
async def submit_report(req: PlayerReportRequest, current_user: User = Depends(get_current_user)):
    """Submits a misconduct report against a player."""
    report_id = moderation_service.file_report(current_user.id, req)
    return {"message": "Report submitted", "report_id": report_id}


@router.post("/ban", dependencies=[Depends(require_role(AccountRole.MODERATOR, AccountRole.ADMIN))])
async def ban_player(req: BanPlayerRequest, current_user: User = Depends(get_current_user)):
    """Applies a ban penalty to a user (Moderator/Admin only)."""
    moderation_service.ban_player(req)
    return {"message": f"Player {req.target_user_id} banned successfully"}
