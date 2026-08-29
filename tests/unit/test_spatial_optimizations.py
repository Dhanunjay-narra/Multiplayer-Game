import pytest
from shared.math import Vector3D, Ray, BoundingBox

def test_fast_distance_squared_and_bounds():
    v1 = Vector3D(0.0, 0.0, 0.0)
    v2 = Vector3D(3.0, 4.0, 0.0)
    assert v1.distance_to(v2) == 5.0

    box = BoundingBox(min_pt=Vector3D(-1.0, -1.0, -1.0), max_pt=Vector3D(1.0, 1.0, 1.0))
    ray = Ray(origin=Vector3D(0.0, 0.0, -5.0), direction=Vector3D(0.0, 0.0, 1.0))
    assert box.intersects_ray(ray) is True

    ray_miss = Ray(origin=Vector3D(0.0, 10.0, -5.0), direction=Vector3D(0.0, 0.0, 1.0))
    assert box.intersects_ray(ray_miss) is False
