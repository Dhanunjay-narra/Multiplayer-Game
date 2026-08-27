"""Unit tests for combat damage calculations, weapons, abilities, and hitscan."""
import pytest
from server.combat.weapons import WEAPON_DEFINITIONS, WeaponType
from server.combat.abilities import ABILITY_DEFINITIONS, AbilityType
from server.combat.damage_calculator import DamageCalculator
from server.combat.hitscan_engine import HitscanEngine
from server.game_server.ecs import EntityManager, Entity, TransformComponent, HealthComponent
from shared.math.vector import Vector3D


def test_weapon_definitions_integrity():
    for wpn_type, stats in WEAPON_DEFINITIONS.items():
        assert stats.base_damage > 0
        assert stats.fire_rate_rpm > 0
        assert stats.effective_range > 0
        assert stats.max_range >= stats.effective_range
        assert stats.headshot_multiplier >= 1.0


def test_damage_distance_falloff():
    rifle = WEAPON_DEFINITIONS[WeaponType.ASSAULT_RIFLE]
    # At 20m (within effective 45m)
    falloff_close = DamageCalculator.calculate_distance_falloff(rifle, 20.0)
    assert falloff_close == 1.0

    # At 90m (max range)
    falloff_far = DamageCalculator.calculate_distance_falloff(rifle, 90.0)
    assert falloff_far == 0.4


def test_headshot_and_armor_mitigation():
    # Base 32, headshot = 32 * 1.75 = 56.0
    dmg_head, is_crit = DamageCalculator.compute_damage(WeaponType.ASSAULT_RIFLE, distance=10.0, hit_location="head")
    assert is_crit is True
    assert dmg_head == 56.0

    # With 100 armor rating: dmg / (1 + 1) = 28.0
    dmg_armored, _ = DamageCalculator.compute_damage(WeaponType.ASSAULT_RIFLE, distance=10.0, hit_location="head", target_armor_rating=100.0)
    assert dmg_armored == 28.0


def test_ability_definitions():
    for ab_type, ab_def in ABILITY_DEFINITIONS.items():
        assert ab_def.cooldown_seconds > 0
        assert ab_def.energy_cost >= 0


def test_hitscan_line_of_sight():
    em = EntityManager()
    target = em.create_entity("target_01", entity_type="player")
    target.add_component(TransformComponent(position=Vector3D(x=0.0, y=0.0, z=50.0)))
    target.add_component(HealthComponent())

    # Shooter fires straight along Z axis towards target
    shooter_origin = Vector3D(x=0.0, y=1.0, z=0.0)
    shooter_aim = Vector3D(x=0.0, y=0.0, z=1.0)

    hit_result = HitscanEngine.trace_shot(em, "shooter_01", shooter_origin, shooter_aim)
    assert hit_result is not None
    target_id, hit_loc, dist = hit_result
    assert target_id == "target_01"
    assert pytest.approx(dist, 1.0) == 50.0
