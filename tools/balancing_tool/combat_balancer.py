"""Combat weapon DPS, TTK (Time-To-Kill), and balance analyzer."""
import os
import sys
from typing import Any, Dict, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from server.combat.weapons import WEAPON_DEFINITIONS, WeaponType


class CombatBalancer:
    """Calculates balance metrics across weapons against varying shield/health targets."""

    @staticmethod
    def calculate_ttk(weapon_type: WeaponType, target_effective_hp: float = 200.0) -> Dict[str, float]:
        stats = WEAPON_DEFINITIONS.get(weapon_type)
        if not stats:
            return {}

        dps = (stats.base_damage * (stats.fire_rate_rpm / 60.0))
        shots_to_kill = -(-target_effective_hp // stats.base_damage)  # Ceil division
        ttk_seconds = (shots_to_kill - 1) * stats.time_between_shots

        return {
            "weapon": stats.name,
            "dps": round(dps, 2),
            "shots_to_kill": int(shots_to_kill),
            "ttk_seconds": round(ttk_seconds, 3),
        }

    @classmethod
    def generate_balance_table(cls) -> List[Dict[str, Any]]:
        table = []
        for wpn_type in WeaponType:
            if wpn_type in WEAPON_DEFINITIONS:
                table.append(cls.calculate_ttk(wpn_type))
        return table


if __name__ == "__main__":
    balancer = CombatBalancer()
    for row in balancer.generate_balance_table():
        print(row)
