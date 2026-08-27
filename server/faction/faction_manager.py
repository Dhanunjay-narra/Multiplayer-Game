"""Faction diplomacy, reputation standing, and territory perks."""
from typing import Dict, Tuple
from shared.enums.game_enums import FactionType, FactionRelation


class FactionManager:
    """Manages persistent faction diplomacy matrices and player reputation ranks."""

    # Default diplomatic relationship matrix
    DIPLOMACY_MATRIX: Dict[Tuple[FactionType, FactionType], FactionRelation] = {
        (FactionType.SOLARIS_HEGEMONY, FactionType.IRON_SYNDICATE): FactionRelation.AT_WAR,
        (FactionType.SOLARIS_HEGEMONY, FactionType.CYBER_NEXUS): FactionRelation.HOSTILE,
        (FactionType.SOLARIS_HEGEMONY, FactionType.VOID_OUTCASTS): FactionRelation.HOSTILE,
        (FactionType.SOLARIS_HEGEMONY, FactionType.NEUTRAL): FactionRelation.FRIENDLY,
        
        (FactionType.IRON_SYNDICATE, FactionType.SOLARIS_HEGEMONY): FactionRelation.AT_WAR,
        (FactionType.IRON_SYNDICATE, FactionType.CYBER_NEXUS): FactionRelation.NEUTRAL,
        (FactionType.IRON_SYNDICATE, FactionType.VOID_OUTCASTS): FactionRelation.HOSTILE,
        (FactionType.IRON_SYNDICATE, FactionType.NEUTRAL): FactionRelation.NEUTRAL,
    }

    @classmethod
    def get_relationship(cls, faction_a: FactionType, faction_b: FactionType) -> FactionRelation:
        """Looks up diplomacy between two factions."""
        if faction_a == faction_b:
            return FactionRelation.ALLIED
        return cls.DIPLOMACY_MATRIX.get((faction_a, faction_b), FactionRelation.NEUTRAL)

    @staticmethod
    def get_reputation_tier(reputation_points: int) -> str:
        """Determines standing tier based on accumulated reputation points."""
        if reputation_points < -1000:
            return "HATED"
        if reputation_points < 0:
            return "UNFRIENDLY"
        if reputation_points < 1000:
            return "NEUTRAL"
        if reputation_points < 5000:
            return "HONORED"
        if reputation_points < 15000:
            return "REVERED"
        return "EXALTED"
