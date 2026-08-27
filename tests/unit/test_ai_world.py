"""Unit tests for AI perception, behavior trees, dynamic world, and missions."""
import pytest
from server.ai.perception import PerceptionSensor
from server.ai.behavior_tree import Sequence, Selector, ActionNode, ConditionNode, NodeStatus
from server.world.dynamic_world import DynamicWorldEngine
from server.mission.mission_engine import DynamicMissionEngine
from shared.math.vector import Vector3D
from shared.enums.game_enums import MissionType, MissionStatus


def test_ai_perception_vision_cone():
    origin = Vector3D(x=0.0, y=0.0, z=0.0)
    forward_yaw = 0.0  # Facing positive Z

    # Target straight ahead at 30m
    target_front = Vector3D(x=0.0, y=0.0, z=30.0)
    assert PerceptionSensor.is_in_vision_cone(origin, forward_yaw, target_front, fov_degrees=90.0) is True

    # Target behind at 30m
    target_behind = Vector3D(x=0.0, y=0.0, z=-30.0)
    assert PerceptionSensor.is_in_vision_cone(origin, forward_yaw, target_behind, fov_degrees=90.0) is False


def test_behavior_tree_evaluation():
    tree = Sequence([
        ConditionNode(lambda ctx: ctx.get("can_act", True)),
        ActionNode(lambda ctx: NodeStatus.SUCCESS),
    ])
    assert tree.tick({"can_act": True}) == NodeStatus.SUCCESS
    assert tree.tick({"can_act": False}) == NodeStatus.FAILURE


def test_dynamic_world_and_territories():
    world = DynamicWorldEngine()
    assert len(world.territories) >= 3
    world.update(delta_time=10.0)
    assert world.time_of_day > 12.0


def test_mission_engine_progression():
    engine = DynamicMissionEngine()
    mission = engine.generate_mission(MissionType.ENERGY_CAPTURE, ["player_01"])
    assert mission.status == MissionStatus.IN_PROGRESS

    # Complete objectives
    for obj in mission.objectives:
        engine.update_objective_progress(mission.mission_id, obj.objective_id, amount=obj.target_count)

    updated_mission = engine.get_mission(mission.mission_id)
    assert updated_mission.status == MissionStatus.COMPLETED
