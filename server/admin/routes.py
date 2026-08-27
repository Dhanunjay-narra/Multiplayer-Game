"""FastAPI endpoints for live-ops configuration and administrative audit."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from server.auth.dependencies import get_current_user, require_role
from server.admin.admin_service import admin_service
from shared.models.db_models import User
from shared.schemas.admin_schemas import LiveGameConfig, AuditLogRecord
from shared.enums.game_enums import AccountRole

router = APIRouter(prefix="/api/v1/admin", tags=["Admin & Live-Ops"])


@router.get("/config", response_model=LiveGameConfig)
async def get_live_config():
    """Returns current live configuration."""
    return admin_service.config


@router.post("/config", response_model=LiveGameConfig, dependencies=[Depends(require_role(AccountRole.ADMIN))])
async def update_live_config(new_config: LiveGameConfig, current_user: User = Depends(get_current_user)):
    """Updates live configuration dynamically without server restart."""
    return admin_service.update_config(new_config, current_user.id)


@router.get("/audit-logs", response_model=List[AuditLogRecord], dependencies=[Depends(require_role(AccountRole.ADMIN))])
async def get_audit_logs():
    """Returns recent administrative audit logs."""
    return admin_service.get_audit_logs()
