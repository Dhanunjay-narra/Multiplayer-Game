"""Data-driven weapon definitions, ballistic calculations, and recoil profiles."""
from typing import Dict
from pydantic import BaseModel
from shared.enums.game_enums import WeaponType, DamageType


class WeaponStats(BaseModel):
    name: str
    weapon_type: WeaponType
    damage_type: DamageType
    base_damage: float
    fire_rate_rpm: float           # Rounds per minute
    effective_range: float         # Max range before falloff (meters)
    max_range: float               # Hard cutoff range
    headshot_multiplier: float
    magazine_capacity: int
    reload_time_seconds: float
    recoil_pitch: float            # Vertical kick per shot
    spread_degrees: float          # Cone of fire angle
    durability_loss_per_shot: float = 0.05

    @property
    def time_between_shots(self) -> float:
        return 60.0 / self.fire_rate_rpm


WEAPON_DEFINITIONS: Dict[WeaponType, WeaponStats] = {
    WeaponType.ASSAULT_RIFLE: WeaponStats(
        name="V-44 Kinetic Liberator",
        weapon_type=WeaponType.ASSAULT_RIFLE,
        damage_type=DamageType.KINETIC,
        base_damage=32.0,
        fire_rate_rpm=650.0,
        effective_range=45.0,
        max_range=90.0,
        headshot_multiplier=1.75,
        magazine_capacity=30,
        reload_time_seconds=2.2,
        recoil_pitch=1.2,
        spread_degrees=1.5,
    ),
    WeaponType.PLASMA_SNIPER: WeaponStats(
        name="Apex Particle Lance",
        weapon_type=WeaponType.PLASMA_SNIPER,
        damage_type=DamageType.ENERGY,
        base_damage=110.0,
        fire_rate_rpm=45.0,
        effective_range=180.0,
        max_range=300.0,
        headshot_multiplier=2.5,
        magazine_capacity=5,
        reload_time_seconds=3.4,
        recoil_pitch=4.5,
        spread_degrees=0.1,
    ),
    WeaponType.SCATTER_SHOTGUN: WeaponStats(
        name="Breacher-12 Slugger",
        weapon_type=WeaponType.SCATTER_SHOTGUN,
        damage_type=DamageType.KINETIC,
        base_damage=95.0,
        fire_rate_rpm=80.0,
        effective_range=15.0,
        max_range=30.0,
        headshot_multiplier=1.5,
        magazine_capacity=8,
        reload_time_seconds=2.8,
        recoil_pitch=3.8,
        spread_degrees=6.0,
    ),
    WeaponType.ARC_CANNON: WeaponStats(
        name="Volt Surge Projector",
        weapon_type=WeaponType.ARC_CANNON,
        damage_type=DamageType.EMP,
        base_damage=48.0,
        fire_rate_rpm=300.0,
        effective_range=35.0,
        max_range=60.0,
        headshot_multiplier=1.2,
        magazine_capacity=20,
        reload_time_seconds=2.5,
        recoil_pitch=0.8,
        spread_degrees=2.0,
    ),
    WeaponType.HEAVY_MG: WeaponStats(
        name="Titan-50 Suppressor",
        weapon_type=WeaponType.HEAVY_MG,
        damage_type=DamageType.EXPLOSIVE,
        base_damage=42.0,
        fire_rate_rpm=550.0,
        effective_range=60.0,
        max_range=120.0,
        headshot_multiplier=1.4,
        magazine_capacity=100,
        reload_time_seconds=5.0,
        recoil_pitch=2.2,
        spread_degrees=3.0,
    ),
    WeaponType.TACTICAL_PISTOL: WeaponStats(
        name="Sidearm Apex-9",
        weapon_type=WeaponType.TACTICAL_PISTOL,
        damage_type=DamageType.KINETIC,
        base_damage=26.0,
        fire_rate_rpm=400.0,
        effective_range=25.0,
        max_range=50.0,
        headshot_multiplier=1.8,
        magazine_capacity=15,
        reload_time_seconds=1.5,
        recoil_pitch=0.9,
        spread_degrees=1.0,
    ),
    WeaponType.ENERGY_BLADE: WeaponStats(
        name="Plasma Edge Katana",
        weapon_type=WeaponType.ENERGY_BLADE,
        damage_type=DamageType.TRUE_DAMAGE,
        base_damage=85.0,
        fire_rate_rpm=120.0,
        effective_range=3.5,
        max_range=4.0,
        headshot_multiplier=1.3,
        magazine_capacity=1,
        reload_time_seconds=0.1,
        recoil_pitch=0.0,
        spread_degrees=0.0,
    ),
}
