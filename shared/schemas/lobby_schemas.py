"""Lobby and party coordination schemas."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from shared.enums.game_enums import CharacterClass, FactionType


class PartyMember(BaseModel):
    player_id: str
    username: str
    is_leader: bool = False
    is_ready: bool = False
    character_class: CharacterClass = CharacterClass.VANGUARD
    faction: FactionType = FactionType.SOLARIS_HEGEMONY
    ping_ms: int = 25


class LobbyCreateRequest(BaseModel):
    lobby_name: str = "Tactical Frontier"
    max_players: int = 16
    selected_map: str = "frontier_nexus_prime"
    is_private: bool = False
    password: Optional[str] = None


class LobbyJoinRequest(BaseModel):
    lobby_id: str
    password: Optional[str] = None


class LobbyState(BaseModel):
    lobby_id: str
    lobby_name: str
    leader_id: str
    max_players: int = 16
    current_players: int = 0
    selected_map: str = "frontier_nexus_prime"
    members: List[PartyMember] = Field(default_factory=list)
    teams: Dict[str, List[str]] = Field(default_factory=dict)  # "Team_A": [player_id, ...], "Team_B": [...]
    is_in_matchmaking: bool = False
    allocated_server_port: Optional[int] = None
