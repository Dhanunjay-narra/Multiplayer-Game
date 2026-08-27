"""Admin live-ops configuration, moderation, and audit logging schemas."""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from shared.enums.game_enums import BanDuration, ReportCategory


class LiveGameConfig(BaseModel):
    version: str = "v1.0.0"
    xp_multiplier: float = 1.0
    energy_harvest_rate_multiplier: float = 1.0
    weapon_damage_scale: float = 1.0
    event_active: bool = False
    active_event_id: Optional[str] = None
    maintenance_mode: bool = False
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)


class BanPlayerRequest(BaseModel):
    target_user_id: str
    reason: str
    duration: BanDuration
    category: ReportCategory


class PlayerReportRequest(BaseModel):
    reported_user_id: str
    category: ReportCategory
    details: str
    match_id: Optional[str] = None


class AuditLogRecord(BaseModel):
    log_id: str
    actor_id: str
    action_type: str
    target_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float
