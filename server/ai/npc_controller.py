"""Tactical NPC AI agent coordinating behavior trees, combat, and territory defense."""
import math
import random
from typing import Any, Dict, List, Optional
from shared.enums.game_enums import FactionType
from shared.math.vector import Vector3D
from server.ai.perception import PerceptionSensor
from server.ai.behavior_tree import BTNode, Sequence, Selector, ActionNode, ConditionNode, NodeStatus


class NPCController:
    """Autonomous AI controller managing perception, combat engagement, and patrol."""

    def __init__(self, npc_id: str, faction: FactionType = FactionType.IRON_SYNDICATE) -> None:
        self.npc_id = npc_id
        self.faction = faction
        self.position = Vector3D.zero()
        self.forward_yaw = 0.0
        self.health = 100.0
        self.target_id: Optional[str] = None
        self.target_position: Optional[Vector3D] = None
        self.is_firing = False
        self.patrol_anchor = Vector3D.zero()
        self.behavior_tree = self._build_behavior_tree()

    def _build_behavior_tree(self) -> BTNode:
        """Constructs tactical behavior tree: Combat -> Investigate -> Patrol."""
        return Selector([
            # 1. Combat Branch
            Sequence([
                ConditionNode(lambda ctx: ctx.get("has_target", False)),
                ActionNode(self._action_engage_target),
            ]),
            # 2. Patrol Branch
            ActionNode(self._action_patrol),
        ])

    def update(self, delta_time: float, nearby_players: List[Dict[str, Any]]) -> None:
        """Scans environment, evaluates threats, and ticks the behavior tree."""
        # Run perception
        highest_threat = 0.0
        best_target = None
        best_pos = None

        for p in nearby_players:
            p_pos: Vector3D = p["position"]
            dist = self.position.distance_to(p_pos)
            in_view = PerceptionSensor.is_in_vision_cone(
                self.position, self.forward_yaw, p_pos, fov_degrees=110.0, max_view_distance=60.0
            )
            if in_view or dist <= 20.0:  # Close proximity awareness
                threat = PerceptionSensor.calculate_threat_score(dist, p.get("health", 100.0), p.get("is_firing", False))
                if threat > highest_threat:
                    highest_threat = threat
                    best_target = p["id"]
                    best_pos = p_pos

        self.target_id = best_target
        self.target_position = best_pos

        context = {
            "has_target": self.target_id is not None,
            "target_pos": self.target_position,
            "delta_time": delta_time,
        }
        self.behavior_tree.tick(context)

    def _action_engage_target(self, context: Dict[str, Any]) -> NodeStatus:
        """Faces target and opens fire within effective combat range."""
        target_pos: Vector3D = context["target_pos"]
        delta_time: float = context["delta_time"]

        dist = self.position.distance_to(target_pos)
        # Face target
        dx = target_pos.x - self.position.x
        dz = target_pos.z - self.position.z
        self.forward_yaw = math.degrees(math.atan2(dx, dz))

        if dist > 15.0:
            # Advance towards target
            dir_vec = (target_pos - self.position).normalized()
            self.position = self.position + (dir_vec * (5.0 * delta_time))
            self.is_firing = False
        else:
            # In combat range, fire weapon
            self.is_firing = True

        return NodeStatus.SUCCESS

    def _action_patrol(self, context: Dict[str, Any]) -> NodeStatus:
        """Patrols around anchor position."""
        self.is_firing = False
        delta_time: float = context["delta_time"]

        dist = self.position.distance_to(self.patrol_anchor)
        if dist > 30.0:
            dir_vec = (self.patrol_anchor - self.position).normalized()
            self.position = self.position + (dir_vec * (3.0 * delta_time))
        return NodeStatus.SUCCESS
