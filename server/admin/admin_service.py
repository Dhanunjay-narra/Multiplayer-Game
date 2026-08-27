"""Admin Live-Ops remote configuration and immutable audit logging."""
import uuid
import time
from typing import Any, Dict, List, Optional
from shared.schemas.admin_schemas import LiveGameConfig, AuditLogRecord


class AdminService:
    """Manages dynamic hot-reloaded game configuration and administrative audit logs."""

    def __init__(self) -> None:
        self.config: LiveGameConfig = LiveGameConfig()
        self.audit_logs: List[AuditLogRecord] = []

    def update_config(self, new_config: LiveGameConfig, admin_id: str) -> LiveGameConfig:
        """Updates live game balance configuration and logs the operation."""
        self.config = new_config
        self.log_action(
            actor_id=admin_id,
            action_type="UPDATE_GAME_CONFIG",
            target_id="global_config",
            details={"version": new_config.version, "xp_mult": new_config.xp_multiplier},
        )
        return self.config

    def log_action(self, actor_id: str, action_type: str, target_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> AuditLogRecord:
        record = AuditLogRecord(
            log_id=f"aud_{uuid.uuid4().hex[:10]}",
            actor_id=actor_id,
            action_type=action_type,
            target_id=target_id,
            details=details or {},
            timestamp=time.time(),
        )
        self.audit_logs.append(record)
        return record

    def get_audit_logs(self, limit: int = 100) -> List[AuditLogRecord]:
        return self.audit_logs[-limit:]


admin_service = AdminService()
