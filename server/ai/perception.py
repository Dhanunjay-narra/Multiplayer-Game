"""Perception system evaluating visual line-of-sight, sound detection, and threat prioritization."""
import math
from typing import Dict, List, Optional
from shared.math.vector import Vector3D
from shared.math.geometry import Ray


class PerceptionSensor:
    """Computes sensory awareness of enemy targets for AI controllers."""

    @staticmethod
    def is_in_vision_cone(
        origin: Vector3D,
        forward_yaw_degrees: float,
        target_pos: Vector3D,
        fov_degrees: float = 90.0,
        max_view_distance: float = 75.0,
    ) -> bool:
        """Evaluates whether target lies within the sensory field of view."""
        dist = origin.distance_to(target_pos)
        if dist > max_view_distance or dist < 0.01:
            return False

        # Compute horizontal angle to target
        dx = target_pos.x - origin.x
        dz = target_pos.z - origin.z
        target_angle_deg = math.degrees(math.atan2(dx, dz))

        angle_diff = abs((target_angle_deg - forward_yaw_degrees + 180) % 360 - 180)
        return angle_diff <= (fov_degrees / 2.0)

    @staticmethod
    def can_hear_noise(
        listener_pos: Vector3D,
        noise_origin: Vector3D,
        noise_loudness_meters: float = 40.0,
    ) -> bool:
        """Determines if acoustic stimulus reaches listener."""
        return listener_pos.distance_to(noise_origin) <= noise_loudness_meters

    @staticmethod
    def calculate_threat_score(
        distance: float,
        target_health: float,
        is_firing: bool,
    ) -> float:
        """Higher threat score = prioritized attack target."""
        score = 100.0 / max(1.0, distance)
        if is_firing:
            score += 50.0
        if target_health < 30.0:  # Prioritize wounded targets
            score += 25.0
        return score
