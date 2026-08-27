"""Raycast hitscan detection and lag compensation against player bounding volumes."""
from typing import Dict, List, Optional, Tuple
from shared.math.vector import Vector3D
from shared.math.geometry import Ray, BoundingBox
from server.game_server.ecs import EntityManager, Entity, TransformComponent, HealthComponent, PlayerComponent


class HitscanEngine:
    """Performs server-side authoritative line-of-sight and ray-hit queries."""

    @staticmethod
    def get_player_hitbox(position: Vector3D) -> Dict[str, BoundingBox]:
        """Constructs separate head and torso hitboxes around player world position."""
        return {
            "head": BoundingBox(
                min_point=Vector3D(x=position.x - 0.25, y=position.y + 1.4, z=position.z - 0.25),
                max_point=Vector3D(x=position.x + 0.25, y=position.y + 1.8, z=position.z + 0.25),
            ),
            "body": BoundingBox(
                min_point=Vector3D(x=position.x - 0.45, y=position.y, z=position.z - 0.45),
                max_point=Vector3D(x=position.x + 0.45, y=position.y + 1.4, z=position.z + 0.45),
            ),
        }

    @classmethod
    def trace_shot(
        cls,
        entity_manager: EntityManager,
        shooter_id: str,
        origin: Vector3D,
        direction: Vector3D,
        max_distance: float = 300.0,
    ) -> Optional[Tuple[str, str, float]]:
        """
        Traces a ray through the world.
        Returns: (target_entity_id, hit_location ["head"|"body"], distance) or None.
        """
        ray = Ray(origin=origin, direction=direction)
        closest_hit: Optional[Tuple[str, str, float]] = None
        closest_dist = max_distance

        for entity in entity_manager.get_entities_with(TransformComponent, HealthComponent):
            if entity.id == shooter_id or not entity.is_active:
                continue

            health = entity.get_component(HealthComponent)
            if not health or not health.is_alive:
                continue

            transform = entity.get_component(TransformComponent)
            if not transform:
                continue

            hitboxes = cls.get_player_hitbox(transform.position)

            # Check head first (for precise headshots)
            head_dist = hitboxes["head"].intersects_ray(ray, max_distance=closest_dist)
            if head_dist is not None and head_dist < closest_dist:
                closest_dist = head_dist
                closest_hit = (entity.id, "head", head_dist)
                continue

            # Check body
            body_dist = hitboxes["body"].intersects_ray(ray, max_distance=closest_dist)
            if body_dist is not None and body_dist < closest_dist:
                closest_dist = body_dist
                closest_hit = (entity.id, "body", body_dist)

        return closest_hit
