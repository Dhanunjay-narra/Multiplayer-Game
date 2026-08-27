"""Match event replay recording and telemetry analytics pipeline."""
import time
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReplayEvent(BaseModel):
    tick: int
    timestamp: float
    event_type: str
    data: Dict[str, Any] = Field(default_factory=dict)


class MatchReplay(BaseModel):
    match_id: str
    map_id: str
    started_at: float
    ended_at: Optional[float] = None
    winning_team: Optional[str] = None
    events: List[ReplayEvent] = Field(default_factory=list)


class ReplayRecorder:
    """Records gameplay event streams for spectators, anti-cheat reviews, and replays."""

    def __init__(self) -> None:
        self.replays: Dict[str, MatchReplay] = {}

    def start_recording(self, match_id: str, map_id: str) -> MatchReplay:
        replay = MatchReplay(match_id=match_id, map_id=map_id, started_at=time.time())
        self.replays[match_id] = replay
        return replay

    def record_event(self, match_id: str, tick: int, event_type: str, data: Dict[str, Any]) -> None:
        replay = self.replays.get(match_id)
        if replay:
            replay.events.append(ReplayEvent(tick=tick, timestamp=time.time(), event_type=event_type, data=data))

    def finish_recording(self, match_id: str, winning_team: str) -> Optional[MatchReplay]:
        replay = self.replays.get(match_id)
        if replay:
            replay.ended_at = time.time()
            replay.winning_team = winning_team
        return replay

    def get_replay(self, match_id: str) -> Optional[MatchReplay]:
        return self.replays.get(match_id)


class AnalyticsService:
    """Aggregates telemetry metrics, DAU/MAU, weapon balance, and win rates."""

    def __init__(self) -> None:
        self.metrics: Dict[str, int] = {
            "total_matches": 0,
            "total_kills": 0,
            "total_territories_captured": 0,
            "total_missions_completed": 0,
        }
        self.weapon_usage: Dict[str, int] = {}

    def record_kill(self, weapon_name: str) -> None:
        self.metrics["total_kills"] += 1
        self.weapon_usage[weapon_name] = self.weapon_usage.get(weapon_name, 0) + 1

    def record_match_completion(self) -> None:
        self.metrics["total_matches"] += 1

    def get_metrics_summary(self) -> Dict[str, Any]:
        return {
            "metrics": self.metrics,
            "weapon_usage": self.weapon_usage,
        }


replay_recorder = ReplayRecorder()
analytics_service = AnalyticsService()
