"""Player moderation, report filing, and account penalties."""
import uuid
import time
from typing import Any, Dict, List, Optional
from shared.schemas.admin_schemas import PlayerReportRequest, BanPlayerRequest
from shared.enums.game_enums import BanDuration, ReportCategory


class ModerationService:
    """Manages community safety, cheat reports, and account bans."""

    def __init__(self) -> None:
        self.reports: List[Dict[str, Any]] = []
        self.active_bans: Dict[str, BanPlayerRequest] = {}

    def file_report(self, reporter_id: str, req: PlayerReportRequest) -> str:
        report_id = f"rep_{uuid.uuid4().hex[:10]}"
        self.reports.append({
            "report_id": report_id,
            "reporter_id": reporter_id,
            "reported_user_id": req.reported_user_id,
            "category": str(req.category),
            "details": req.details,
            "match_id": req.match_id,
            "timestamp": time.time(),
        })
        return report_id

    def ban_player(self, req: BanPlayerRequest) -> None:
        self.active_bans[req.target_user_id] = req

    def is_player_banned(self, user_id: str) -> bool:
        return user_id in self.active_bans


moderation_service = ModerationService()
