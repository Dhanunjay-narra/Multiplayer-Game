"""Progression tracking for Battle Pass seasons, skill trees, and account ranks."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SeasonPassTrack(BaseModel):
    season_id: str = "season_01_frontier_rising"
    season_name: str = "Season 1: Frontier Rising"
    current_tier: int = 1
    max_tier: int = 100
    tier_xp: int = 0
    xp_per_tier: int = 2000
    is_premium: bool = False


class ProgressionService:
    """Manages seasonal battle pass milestones, tier rewards, and skill trees."""

    def __init__(self) -> None:
        self.player_passes: Dict[str, SeasonPassTrack] = {}

    def get_or_create_pass(self, user_id: str) -> SeasonPassTrack:
        if user_id not in self.player_passes:
            self.player_passes[user_id] = SeasonPassTrack()
        return self.player_passes[user_id]

    def add_season_xp(self, user_id: str, xp_amount: int) -> int:
        """Adds season XP and increments battle pass tiers."""
        sp = self.get_or_create_pass(user_id)
        sp.tier_xp += xp_amount
        while sp.tier_xp >= sp.xp_per_tier and sp.current_tier < sp.max_tier:
            sp.tier_xp -= sp.xp_per_tier
            sp.current_tier += 1
        return sp.current_tier


progression_service = ProgressionService()
