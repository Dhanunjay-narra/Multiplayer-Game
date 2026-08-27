"""Player character, statistics, and loadout schemas."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from shared.enums.game_enums import CharacterClass, FactionType, RankTier, WeaponType, AbilityType


class CharacterCreateRequest(BaseModel):
    character_name: str = Field(..., min_length=2, max_length=24)
    character_class: CharacterClass
    faction: FactionType


class LoadoutItemSlot(BaseModel):
    slot_name: str  # "primary_weapon", "secondary_weapon", "ability_1", "ability_2", "armor"
    item_id: str


class LoadoutConfig(BaseModel):
    loadout_id: str
    name: str = "Default Loadout"
    primary_weapon: WeaponType = WeaponType.ASSAULT_RIFLE
    secondary_weapon: WeaponType = WeaponType.TACTICAL_PISTOL
    primary_ability: AbilityType = AbilityType.SHIELD_DOME
    secondary_ability: AbilityType = AbilityType.RECON_RADAR


class PlayerStats(BaseModel):
    matches_played: int = 0
    matches_won: int = 0
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    territories_captured: int = 0
    missions_completed: int = 0
    resources_extracted: float = 0.0
    total_damage_dealt: float = 0.0

    @property
    def win_rate(self) -> float:
        return (self.matches_won / self.matches_played) if self.matches_played > 0 else 0.0

    @property
    def kda_ratio(self) -> float:
        return ((self.kills + self.assists) / max(1, self.deaths))


class PlayerProfile(BaseModel):
    player_id: str
    username: str
    avatar_url: Optional[str] = None
    level: int = 1
    current_xp: int = 0
    next_level_xp: int = 1000
    rank_tier: RankTier = RankTier.UNRANKED
    rank_points: int = 0
    active_faction: FactionType = FactionType.SOLARIS_HEGEMONY
    faction_reputations: Dict[FactionType, int] = Field(default_factory=dict)
    stats: PlayerStats = Field(default_factory=PlayerStats)
    active_loadout: LoadoutConfig = Field(default_factory=lambda: LoadoutConfig(loadout_id="loadout_default"))
