"""Dedicated server network session manager, packet handling, and anti-cheat validation."""
from __future__ import annotations
import asyncio
import time
import json
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set
from shared.enums.game_enums import PacketOpcode, DisconnectReason
from shared.protocols.packet import GamePacket, PacketHeader, SequenceTracker
from shared.schemas.gameplay_schemas import PlayerInput
from shared.constants.game_constants import (
    MAX_INPUTS_PER_SECOND,
    MAX_ALLOWED_SPEED_TOLERANCE,
    MAX_TELEPORT_DISTANCE_PER_TICK,
    BASE_WALK_SPEED,
    SPRINT_SPEED_MULTIPLIER,
)
from shared.math.vector import Vector3D

logger = logging.getLogger("nexus.server.networking")


class ClientSession:
    """Represents a connected client session on the dedicated server."""
    def __init__(self, player_id: str, username: str, connection: Any = None) -> None:
        self.player_id: str = player_id
        self.username: str = username
        self.connection: Any = connection  # WebSocket or custom socket adapter
        self.sequence_tracker: SequenceTracker = SequenceTracker()
        self.last_heard_time: float = time.time()
        self.ping_ms: int = 25
        self.input_history: List[PlayerInput] = []
        self.recent_input_timestamps: List[float] = []
        self.last_validated_position: Optional[Vector3D] = None
        self.anti_cheat_violations: int = 0
        self.is_authenticated: bool = False

    def record_input(self, player_input: PlayerInput) -> bool:
        """Validates input rate against DDoS / packet spam anti-cheat rules."""
        now = time.time()
        self.last_heard_time = now
        self.recent_input_timestamps.append(now)
        # Keep window of 1 second
        self.recent_input_timestamps = [t for t in self.recent_input_timestamps if now - t <= 1.0]

        if len(self.recent_input_timestamps) > MAX_INPUTS_PER_SECOND:
            self.anti_cheat_violations += 1
            logger.warning(f"Anti-Cheat: Player {self.player_id} exceeded max inputs/sec ({len(self.recent_input_timestamps)})")
            return False

        self.input_history.append(player_input)
        if len(self.input_history) > 120:
            self.input_history = self.input_history[-60:]
        return True


class NetworkManager:
    """Coordinates all inbound and outbound client communications."""
    def __init__(self) -> None:
        self.sessions: Dict[str, ClientSession] = {}
        self._inbound_packet_queue: asyncio.Queue[GamePacket] = asyncio.Queue()

    def register_client(self, player_id: str, username: str, connection: Any = None) -> ClientSession:
        session = ClientSession(player_id=player_id, username=username, connection=connection)
        self.sessions[player_id] = session
        logger.info(f"Client registered: {username} ({player_id})")
        return session

    def unregister_client(self, player_id: str) -> Optional[ClientSession]:
        session = self.sessions.pop(player_id, None)
        if session:
            logger.info(f"Client disconnected: {session.username} ({player_id})")
        return session

    def get_session(self, player_id: str) -> Optional[ClientSession]:
        return self.sessions.get(player_id)

    async def enqueue_packet(self, packet: GamePacket) -> None:
        await self._inbound_packet_queue.put(packet)

    async def poll_inbound_packets(self, max_batch: int = 100) -> List[GamePacket]:
        packets: List[GamePacket] = []
        for _ in range(max_batch):
            if self._inbound_packet_queue.empty():
                break
            try:
                packets.append(self._inbound_packet_queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        return packets

    async def send_packet(self, player_id: str, opcode: PacketOpcode, payload: Dict[str, Any], reliable: bool = False) -> None:
        session = self.sessions.get(player_id)
        if not session or not session.connection:
            return

        seq = session.sequence_tracker.get_next_sequence()
        header = PacketHeader(
            opcode=opcode,
            sequence=seq,
            ack=session.sequence_tracker.highest_remote_sequence,
            ack_bitfield=session.sequence_tracker.ack_bitfield,
            sender_id="server",
        )
        packet = GamePacket(header=header, payload=payload, is_reliable=reliable)

        try:
            # Check if WebSocket
            if hasattr(session.connection, "send_text"):
                await session.connection.send_text(packet.serialize_json())
            elif hasattr(session.connection, "send"):
                await session.connection.send(packet.serialize_json())
        except Exception as e:
            logger.error(f"Failed to send packet to {player_id}: {e}")

    async def broadcast_packet(self, opcode: PacketOpcode, payload: Dict[str, Any], exclude_player_id: Optional[str] = None) -> None:
        """Broadcasts a packet to all connected clients."""
        tasks = []
        for pid, session in self.sessions.items():
            if exclude_player_id and pid == exclude_player_id:
                continue
            tasks.append(self.send_packet(pid, opcode, payload, reliable=False))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def validate_movement_delta(
        self,
        session: ClientSession,
        current_pos: Vector3D,
        target_pos: Vector3D,
        delta_time: float,
        is_sprinting: bool,
    ) -> bool:
        """Server-side authoritative movement and anti-teleport check."""
        displacement = current_pos.distance_to(target_pos)
        max_speed = (BASE_WALK_SPEED * SPRINT_SPEED_MULTIPLIER if is_sprinting else BASE_WALK_SPEED) * MAX_ALLOWED_SPEED_TOLERANCE
        max_allowed_dist = max_speed * delta_time + 0.5  # 0.5m buffer for frame variance

        if displacement > MAX_TELEPORT_DISTANCE_PER_TICK or displacement > max_allowed_dist:
            session.anti_cheat_violations += 1
            logger.warning(
                f"Anti-Cheat: Player {session.player_id} moved {displacement:.2f}m in {delta_time:.3f}s (max allowed: {max_allowed_dist:.2f}m)"
            )
            return False

        session.last_validated_position = target_pos
        return True
