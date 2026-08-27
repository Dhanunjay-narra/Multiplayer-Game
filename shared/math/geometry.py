"""Spatial bounds, raycasting, and collision detection primitives."""
from __future__ import annotations
import math
from typing import Optional, Tuple
from pydantic import BaseModel
from shared.math.vector import Vector3D


class Ray(BaseModel):
    """Ray defined by an origin and a normalized direction."""
    origin: Vector3D
    direction: Vector3D

    def model_post_init(self, __context) -> None:
        object.__setattr__(self, 'direction', self.direction.normalized())

    def point_at(self, distance: float) -> Vector3D:
        return self.origin + (self.direction * distance)


class BoundingBox(BaseModel):
    """Axis-Aligned Bounding Box (AABB) for spatial partitioning and hitboxes."""
    min_point: Vector3D
    max_point: Vector3D

    def contains(self, point: Vector3D) -> bool:
        return (
            self.min_point.x <= point.x <= self.max_point.x and
            self.min_point.y <= point.y <= self.max_point.y and
            self.min_point.z <= point.z <= self.max_point.z
        )

    def intersects(self, other: BoundingBox) -> bool:
        return (
            self.min_point.x <= other.max_point.x and self.max_point.x >= other.min_point.x and
            self.min_point.y <= other.max_point.y and self.max_point.y >= other.min_point.y and
            self.min_point.z <= other.max_point.z and self.max_point.z >= other.min_point.z
        )

    def intersects_ray(self, ray: Ray, max_distance: float = 1000.0) -> Optional[float]:
        """Slab method for ray-AABB intersection. Returns distance to hit or None."""
        t_min = 0.0
        t_max = max_distance

        for i in ['x', 'y', 'z']:
            origin_val = getattr(ray.origin, i)
            dir_val = getattr(ray.direction, i)
            min_val = getattr(self.min_point, i)
            max_val = getattr(self.max_point, i)

            if abs(dir_val) < 1e-6:
                if origin_val < min_val or origin_val > max_val:
                    return None
            else:
                t1 = (min_val - origin_val) / dir_val
                t2 = (max_val - origin_val) / dir_val

                if t1 > t2:
                    t1, t2 = t2, t1

                t_min = max(t_min, t1)
                t_max = min(t_max, t2)

                if t_min > t_max:
                    return None

        return t_min if t_min <= max_distance else None


class Sphere(BaseModel):
    """Bounding sphere for fast broadphase collision and explosion radiuses."""
    center: Vector3D
    radius: float

    def contains(self, point: Vector3D) -> bool:
        return self.center.distance_to(point) <= self.radius

    def intersects(self, other: Sphere) -> bool:
        dist = self.center.distance_to(other.center)
        return dist <= (self.radius + other.radius)

    def intersects_ray(self, ray: Ray, max_distance: float = 1000.0) -> Optional[float]:
        """Ray-Sphere intersection test."""
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return None

        t = (-b - math.sqrt(discriminant)) / (2.0 * a)
        if t >= 0 and t <= max_distance:
            return t
        
        t = (-b + math.sqrt(discriminant)) / (2.0 * a)
        if t >= 0 and t <= max_distance:
            return t

        return None
