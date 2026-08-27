"""Character tactical abilities, cooldowns, and status effect handlers."""
from typing import Dict, Optional
from pydantic import BaseModel
from shared.enums.game_enums import AbilityType, DamageType


class AbilityDefinition(BaseModel):
    name: str
    ability_type: AbilityType
    cooldown_seconds: float
    duration_seconds: float
    energy_cost: float
    radius_meters: float
    effect_value: float  # e.g., shield HP, heal rate/sec, radar range
    description: str


ABILITY_DEFINITIONS: Dict[AbilityType, AbilityDefinition] = {
    AbilityType.SHIELD_DOME: AbilityDefinition(
        name="Aegis Fortification Dome",
        ability_type=AbilityType.SHIELD_DOME,
        cooldown_seconds=30.0,
        duration_seconds=12.0,
        energy_cost=40.0,
        radius_meters=6.0,
        effect_value=500.0,  # 500 shield HP barrier
        description="Deploys an impenetrable energy dome absorbing incoming ballistic fire.",
    ),
    AbilityType.RECON_RADAR: AbilityDefinition(
        name="Tactical Sonar Sweep",
        ability_type=AbilityType.RECON_RADAR,
        cooldown_seconds=20.0,
        duration_seconds=6.0,
        energy_cost=25.0,
        radius_meters=75.0,
        effect_value=1.0,
        description="Emits a sensory pulse revealing all enemy positions within 75 meters.",
    ),
    AbilityType.EMP_BURST: AbilityDefinition(
        name="Ion Disruptor Shockwave",
        ability_type=AbilityType.EMP_BURST,
        cooldown_seconds=35.0,
        duration_seconds=4.0,
        energy_cost=50.0,
        radius_meters=18.0,
        effect_value=100.0,  # Drains 100 shield instantly and disables abilities for 4s
        description="Unleashes an electromagnetic burst stripping shields and disabling tech.",
    ),
    AbilityType.TELEPORT_BEACON: AbilityDefinition(
        name="Quantum Displacement Beacon",
        ability_type=AbilityType.TELEPORT_BEACON,
        cooldown_seconds=25.0,
        duration_seconds=15.0,
        energy_cost=30.0,
        radius_meters=50.0,
        effect_value=0.0,
        description="Drops a quantum anchor allowing instant recall within 15 seconds.",
    ),
    AbilityType.NANO_HEAL_FIELD: AbilityDefinition(
        name="Nanite Restoration Matrix",
        ability_type=AbilityType.NANO_HEAL_FIELD,
        cooldown_seconds=22.0,
        duration_seconds=8.0,
        energy_cost=35.0,
        radius_meters=8.0,
        effect_value=25.0,  # 25 HP / sec healing
        description="Creates an area of effect healing all allies within 8 meters.",
    ),
    AbilityType.ATTACK_DRONE: AbilityDefinition(
        name="Autonomous Sentinel Drone",
        ability_type=AbilityType.ATTACK_DRONE,
        cooldown_seconds=40.0,
        duration_seconds=20.0,
        energy_cost=60.0,
        radius_meters=25.0,
        effect_value=15.0,  # Damage per shot
        description="Deploys an automated hovering drone that fires at detected hostiles.",
    ),
    AbilityType.CLOAKING: AbilityDefinition(
        name="Optical Camouflage",
        ability_type=AbilityType.CLOAKING,
        cooldown_seconds=25.0,
        duration_seconds=8.0,
        energy_cost=30.0,
        radius_meters=0.0,
        effect_value=1.0,
        description="Renders operative invisible to enemy vision cones for 8 seconds.",
    ),
    AbilityType.FORTIFY_NODE: AbilityDefinition(
        name="Nexus Overclock Surge",
        ability_type=AbilityType.FORTIFY_NODE,
        cooldown_seconds=45.0,
        duration_seconds=30.0,
        energy_cost=50.0,
        radius_meters=35.0,
        effect_value=2.0,  # 2x extraction rate
        description="Doubles the energy extraction rate of a captured territory node.",
    ),
}
