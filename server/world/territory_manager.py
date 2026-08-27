"""Territory ownership, defense fortifications, and persistent faction influence."""
from typing import Dict, List, Optional
from shared.enums.game_enums import FactionType, TerritoryState
from shared.schemas.world_schemas import TerritoryStateData
from shared.math.vector import Vector3D


class TerritoryManager:
    """Handles territory captures, defense fortification upgrades, and sabotage."""

    def __init__(self, territories: Optional[Dict[str, TerritoryStateData]] = None) -> None:
        self.territories: Dict[str, TerritoryStateData] = territories or {}

    def capture_territory(self, territory_id: str, claiming_faction: FactionType) -> bool:
        """Transfers ownership of a territory to the victorious faction."""
        terr = self.territories.get(territory_id)
        if not terr:
            return False

        terr.controlling_faction = claiming_faction
        terr.state = TerritoryState.FORTIFIED
        terr.capture_progress = 100.0
        return True

    def upgrade_defense(self, territory_id: str) -> int:
        """Upgrades defense rating of a held territory up to level 5."""
        terr = self.territories.get(territory_id)
        if not terr or terr.controlling_faction == FactionType.NEUTRAL:
            return 0

        if terr.defense_level < 5:
            terr.defense_level += 1
        return terr.defense_level

    def sabotage_territory(self, territory_id: str) -> bool:
        """Reduces defense level and sets state to vulnerable."""
        terr = self.territories.get(territory_id)
        if not terr:
            return False

        terr.defense_level = max(1, terr.defense_level - 1)
        terr.state = TerritoryState.VULNERABLE
        return True

    def get_faction_territory_count(self, faction: FactionType) -> int:
        """Returns total territories currently controlled by a faction."""
        return sum(1 for t in self.territories.values() if t.controlling_faction == faction)
