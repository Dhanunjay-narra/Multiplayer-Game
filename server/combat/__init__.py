"""Nexus Frontier Combat Package."""
from server.combat.weapons import WEAPON_DEFINITIONS, WeaponStats
from server.combat.abilities import ABILITY_DEFINITIONS, AbilityDefinition
from server.combat.damage_calculator import DamageCalculator
from server.combat.hitscan_engine import HitscanEngine

__all__ = [
    "WEAPON_DEFINITIONS",
    "WeaponStats",
    "ABILITY_DEFINITIONS",
    "AbilityDefinition",
    "DamageCalculator",
    "HitscanEngine",
]
