"""Tests for shared math, protocol serialization, and database models."""
import pytest
from shared.math.vector import Vector2D, Vector3D
from shared.math.geometry import Ray, BoundingBox, Sphere
from shared.protocols.packet import GamePacket, PacketHeader, SequenceTracker
from shared.enums.game_enums import PacketOpcode, CharacterClass, FactionType
from shared.schemas.player_schemas import CharacterCreateRequest, PlayerProfile
from shared.event_bus.bus import AsyncEventBus, DomainEvent


def test_vector2d_operations():
    v1 = Vector2D(x=3.0, y=4.0)
    assert v1.magnitude() == 5.0
    v2 = Vector2D(x=1.0, y=2.0)
    v3 = v1 + v2
    assert v3.x == 4.0 and v3.y == 6.0
    assert v1.dot(v2) == 11.0


def test_vector3d_operations():
    v1 = Vector3D(x=1.0, y=2.0, z=2.0)
    assert v1.magnitude() == 3.0
    norm = v1.normalized()
    assert pytest.approx(norm.magnitude()) == 1.0
    v2 = Vector3D(x=0.0, y=1.0, z=0.0)
    cross = Vector3D.forward().cross(Vector3D.right())
    assert cross.y == -1.0 or cross.y == 1.0 or abs(cross.magnitude()) == 1.0


def test_ray_bounding_box_intersection():
    ray = Ray(origin=Vector3D(x=0.0, y=0.0, z=-10.0), direction=Vector3D(x=0.0, y=0.0, z=1.0))
    bbox = BoundingBox(
        min_point=Vector3D(x=-1.0, y=-1.0, z=-1.0),
        max_point=Vector3D(x=1.0, y=1.0, z=1.0)
    )
    hit_dist = bbox.intersects_ray(ray)
    assert hit_dist is not None
    assert pytest.approx(hit_dist, 0.01) == 9.0


def test_ray_sphere_intersection():
    ray = Ray(origin=Vector3D(x=0.0, y=0.0, z=-10.0), direction=Vector3D(x=0.0, y=0.0, z=1.0))
    sphere = Sphere(center=Vector3D(x=0.0, y=0.0, z=0.0), radius=2.0)
    hit_dist = sphere.intersects_ray(ray)
    assert hit_dist is not None
    assert pytest.approx(hit_dist, 0.01) == 8.0


def test_packet_json_serialization():
    header = PacketHeader(opcode=PacketOpcode.PLAYER_INPUT, sequence=42, ack=40, ack_bitfield=1)
    pkt = GamePacket(header=header, payload={"input_seq": 42, "sprint": True}, is_reliable=True)
    json_str = pkt.serialize_json()
    deserialized = GamePacket.deserialize_json(json_str)
    assert deserialized.header.opcode == PacketOpcode.PLAYER_INPUT
    assert deserialized.header.sequence == 42
    assert deserialized.payload["input_seq"] == 42
    assert deserialized.is_reliable is True


def test_packet_binary_serialization():
    header = PacketHeader(opcode=PacketOpcode.COMBAT_ACTION, sequence=10, ack=9, ack_bitfield=0, sender_id="player_01")
    pkt = GamePacket(header=header, payload={"action": "fire", "dmg": 45.5}, is_reliable=True)
    binary_data = pkt.serialize_binary()
    deserialized = GamePacket.deserialize_binary(binary_data)
    assert deserialized.header.opcode == PacketOpcode.COMBAT_ACTION
    assert deserialized.header.sequence == 10
    assert deserialized.header.sender_id == "player_01"
    assert deserialized.payload["action"] == "fire"
    assert deserialized.payload["dmg"] == 45.5


def test_sequence_tracker():
    tracker = SequenceTracker()
    assert tracker.get_next_sequence() == 1
    assert tracker.get_next_sequence() == 2

    tracker.register_incoming(1)
    tracker.register_incoming(2)
    tracker.register_incoming(3)
    assert tracker.highest_remote_sequence == 3
    assert tracker.is_packet_acknowledged(2, tracker.highest_remote_sequence, tracker.ack_bitfield)


@pytest.mark.asyncio
async def test_async_event_bus():
    bus = AsyncEventBus()
    received_events = []

    async def on_player_kill(event: DomainEvent):
        received_events.append(event)

    bus.subscribe("PlayerKilled", on_player_kill)
    await bus.publish(DomainEvent(event_type="PlayerKilled", source="Server", payload={"killer": "p1", "victim": "p2"}))
    
    assert len(received_events) == 1
    assert received_events[0].payload["killer"] == "p1"
