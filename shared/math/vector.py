"""High-performance vector math operations for 2D and 3D game coordinates."""
from __future__ import annotations
import math
from typing import Tuple, Union
from pydantic import BaseModel, Field


class Vector2D(BaseModel):
    """2D Vector for planar calculations, radar, and navigation."""
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: Union[Vector2D, float]) -> Vector2D:
        if isinstance(other, Vector2D):
            return Vector2D(x=self.x + other.x, y=self.y + other.y)
        return Vector2D(x=self.x + other, y=self.y + other)

    def __sub__(self, other: Union[Vector2D, float]) -> Vector2D:
        if isinstance(other, Vector2D):
            return Vector2D(x=self.x - other.x, y=self.y - other.y)
        return Vector2D(x=self.x - other, y=self.y - other)

    def __mul__(self, scalar: float) -> Vector2D:
        return Vector2D(x=self.x * scalar, y=self.y * scalar)

    def __truediv__(self, scalar: float) -> Vector2D:
        if scalar == 0:
            return Vector2D(x=0.0, y=0.0)
        return Vector2D(x=self.x / scalar, y=self.y / scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def magnitude_sq(self) -> float:
        return self.x * self.x + self.y * self.y

    def normalized(self) -> Vector2D:
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(x=0.0, y=0.0)
        return Vector2D(x=self.x / mag, y=self.y / mag)

    def distance_to(self, other: Vector2D) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def dot(self, other: Vector2D) -> float:
        return self.x * other.x + self.y * other.y

    def lerp(self, target: Vector2D, t: float) -> Vector2D:
        t = max(0.0, min(1.0, t))
        return Vector2D(
            x=self.x + (target.x - self.x) * t,
            y=self.y + (target.y - self.y) * t,
        )

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


class Vector3D(BaseModel):
    """3D Vector for spatial orientation, player positions, and raycasting."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: Union[Vector3D, float]) -> Vector3D:
        if isinstance(other, Vector3D):
            return Vector3D(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)
        return Vector3D(x=self.x + other, y=self.y + other, z=self.z + other)

    def __sub__(self, other: Union[Vector3D, float]) -> Vector3D:
        if isinstance(other, Vector3D):
            return Vector3D(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)
        return Vector3D(x=self.x - other, y=self.y - other, z=self.z - other)

    def __mul__(self, scalar: float) -> Vector3D:
        return Vector3D(x=self.x * scalar, y=self.y * scalar, z=self.z * scalar)

    def __truediv__(self, scalar: float) -> Vector3D:
        if scalar == 0:
            return Vector3D(x=0.0, y=0.0, z=0.0)
        return Vector3D(x=self.x / scalar, y=self.y / scalar, z=self.z / scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def magnitude_sq(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z

    def normalized(self) -> Vector3D:
        mag = self.magnitude()
        if mag == 0:
            return Vector3D(x=0.0, y=0.0, z=0.0)
        return Vector3D(x=self.x / mag, y=self.y / mag, z=self.z / mag)

    def distance_to(self, other: Vector3D) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def dot(self, other: Vector3D) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vector3D) -> Vector3D:
        return Vector3D(
            x=self.y * other.z - self.z * other.y,
            y=self.z * other.x - self.x * other.z,
            z=self.x * other.y - self.y * other.x,
        )

    def lerp(self, target: Vector3D, t: float) -> Vector3D:
        t = max(0.0, min(1.0, t))
        return Vector3D(
            x=self.x + (target.x - self.x) * t,
            y=self.y + (target.y - self.y) * t,
            z=self.z + (target.z - self.z) * t,
        )

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    @classmethod
    def zero(cls) -> Vector3D:
        return cls(x=0.0, y=0.0, z=0.0)

    @classmethod
    def up(cls) -> Vector3D:
        return cls(x=0.0, y=1.0, z=0.0)

    @classmethod
    def forward(cls) -> Vector3D:
        return cls(x=0.0, y=0.0, z=1.0)

    @classmethod
    def right(cls) -> Vector3D:
        return cls(x=1.0, y=0.0, z=0.0)
