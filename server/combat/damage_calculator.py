"""Combat damage calculations, distance falloff, armor mitigation, and status effects."""
from typing import Dict, Tuple
from shared.enums.game_enums import WeaponType, DamageType
from server.combat.weapons import WEAPON_DEFINITIONS, WeaponStats


class DamageCalculator:
    """Computes exact damage values with physics falloff and armor mitigations."""

    @staticmethod
    def calculate_distance_falloff(weapon_stats: WeaponStats, distance: float) -> float:
        """Applies linear dropoff beyond effective range down to 40% base damage at max range."""
        if distance <= weapon_stats.effective_range:
            return 1.0
        if distance >= weapon_stats.max_range:
            return 0.4
        
        range_span = weapon_stats.max_range - weapon_stats.effective_range
        excess_dist = distance - weapon_stats.effective_range
        falloff_factor = 1.0 - (0.6 * (excess_dist / range_span))
        return max(0.4, min(1.0, falloff_factor))

    @classmethod
    def compute_damage(
        cls,
        weapon_type: WeaponType,
        distance: float,
        hit_location: str = "body",
        target_armor_rating: float = 0.0,
    ) -> Tuple[float, bool]:
        """Calculates final mitigated damage and whether the shot was critical."""
        weapon = WEAPON_DEFINITIONS.get(weapon_type)
        if not weapon:
            return (20.0, False)

        falloff = cls.calculate_distance_falloff(weapon, distance)
        raw_damage = weapon.base_damage * falloff

        is_headshot = hit_location.lower() == "head"
        if is_headshot:
            raw_damage *= weapon.headshot_multiplier

        # Armor mitigation: Damage = Raw / (1 + Armor / 100)
        mitigated_damage = raw_damage / (1.0 + (target_armor_rating / 100.0))
        return (round(mitigated_damage, 2), is_headshot)
