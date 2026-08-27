"""Matchmaking queue and dedicated server reservation schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field
from shared.enums.game_enums import RankTier


class MatchmakingTicket(BaseModel):
    ticket_id: str
    player_id: str
    username: str
    party_id: Optional[str] = None
    party_members: List[str] = Field(default_factory=list)
    rank_tier: RankTier = RankTier.UNRANKED
    mmr: int = 1200
    region: str = "us-east"
    created_at: float
    matched: bool = False
    match_id: Optional[str] = None


class MatchReservation(BaseModel):
    match_id: str
    map_id: str
    server_address: str
    server_port: int
    auth_token: str
    assigned_team: str
    player_ids: List[str]
    expires_at: float


class ServerAllocationRequest(BaseModel):
    match_id: str
    map_id: str
    team_a_players: List[str]
    team_b_players: List[str]
    region: str = "us-east"
