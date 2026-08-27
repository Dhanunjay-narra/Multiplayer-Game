"""Social network, friends, chat, and clan schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field
from shared.enums.game_enums import FactionType, RankTier


class FriendRecord(BaseModel):
    friend_id: str
    username: str
    is_online: bool = False
    current_activity: str = "In Main Menu"
    rank_tier: RankTier = RankTier.UNRANKED


class ClanMemberRecord(BaseModel):
    user_id: str
    username: str
    role: str = "MEMBER"  # "LEADER", "OFFICER", "MEMBER", "RECRUIT"
    contributed_xp: int = 0
    joined_at: float


class ClanData(BaseModel):
    clan_id: str
    name: str
    tag: str
    faction_alignment: FactionType = FactionType.SOLARIS_HEGEMONY
    level: int = 1
    total_reputation: int = 0
    members: List[ClanMemberRecord] = Field(default_factory=list)
    motd: str = "Welcome to Nexus Frontier"


class ChatMessageData(BaseModel):
    message_id: str
    sender_id: str
    sender_name: str
    channel: str  # "GLOBAL", "PARTY", "TEAM", "CLAN", "PROXIMITY"
    content: str
    timestamp: float
