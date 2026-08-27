"""Network packet framing, serialization, sequence tracking, and acknowledgement handling."""
from __future__ import annotations
import json
import struct
import time
import zlib
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from shared.enums.game_enums import PacketOpcode


class PacketHeader(BaseModel):
    """Network header attached to every game packet."""
    opcode: PacketOpcode
    sequence: int = 0
    ack: int = 0
    ack_bitfield: int = 0
    timestamp: float = Field(default_factory=lambda: time.time() * 1000.0)
    sender_id: Optional[str] = None


class GamePacket(BaseModel):
    """Unified Game Packet container."""
    header: PacketHeader
    payload: Dict[str, Any] = Field(default_factory=dict)
    is_reliable: bool = False

    def serialize_json(self) -> str:
        """Serializes the packet to a compact JSON string."""
        return json.dumps({
            "op": int(self.header.opcode),
            "seq": self.header.sequence,
            "ack": self.header.ack,
            "abf": self.header.ack_bitfield,
            "ts": round(self.header.timestamp, 2),
            "sid": self.header.sender_id,
            "rel": self.is_reliable,
            "data": self.payload,
        })

    @classmethod
    def deserialize_json(cls, raw_json: str) -> GamePacket:
        """Deserializes a JSON string into a GamePacket."""
        data = json.loads(raw_json)
        return cls(
            header=PacketHeader(
                opcode=PacketOpcode(data["op"]),
                sequence=data.get("seq", 0),
                ack=data.get("ack", 0),
                ack_bitfield=data.get("abf", 0),
                timestamp=data.get("ts", time.time() * 1000.0),
                sender_id=data.get("sid"),
            ),
            payload=data.get("data", {}),
            is_reliable=data.get("rel", False),
        )

    def serialize_binary(self) -> bytes:
        """
        Binary packet format:
        [2 bytes opcode][4 bytes seq][4 bytes ack][4 bytes ack_bitfield][8 bytes timestamp][payload json compressed]
        """
        json_data = json.dumps(self.payload).encode("utf-8")
        compressed_payload = zlib.compress(json_data)
        
        sender_bytes = (self.header.sender_id or "").encode("utf-8")[:32].ljust(32, b'\x00')
        
        header_bytes = struct.pack(
            "!HIII d 32s ?",
            int(self.header.opcode),
            self.header.sequence,
            self.header.ack,
            self.header.ack_bitfield,
            self.header.timestamp,
            sender_bytes,
            self.is_reliable
        )
        return header_bytes + compressed_payload

    @classmethod
    def deserialize_binary(cls, raw_bytes: bytes) -> GamePacket:
        """Deserializes binary bytes into a GamePacket."""
        header_size = struct.calcsize("!HIII d 32s ?")
        if len(raw_bytes) < header_size:
            raise ValueError(f"Packet too short for header: {len(raw_bytes)} bytes")

        opcode_val, seq, ack, abf, ts, sender_raw, rel = struct.unpack(
            "!HIII d 32s ?",
            raw_bytes[:header_size]
        )
        
        sender_id = sender_raw.rstrip(b'\x00').decode("utf-8", errors="ignore") or None
        compressed_payload = raw_bytes[header_size:]
        
        if compressed_payload:
            payload_data = json.loads(zlib.decompress(compressed_payload).decode("utf-8"))
        else:
            payload_data = {}

        return cls(
            header=PacketHeader(
                opcode=PacketOpcode(opcode_val),
                sequence=seq,
                ack=ack,
                ack_bitfield=abf,
                timestamp=ts,
                sender_id=sender_id,
            ),
            payload=payload_data,
            is_reliable=rel,
        )


class SequenceTracker:
    """Tracks outgoing sequence numbers and computes incoming ACK bitfields."""
    def __init__(self) -> None:
        self.next_sequence: int = 1
        self.highest_remote_sequence: int = 0
        self.ack_bitfield: int = 0

    def get_next_sequence(self) -> int:
        seq = self.next_sequence
        self.next_sequence += 1
        return seq

    def register_incoming(self, sequence: int) -> None:
        """Updates highest received sequence and shifts bitfield."""
        if sequence > self.highest_remote_sequence:
            shift = sequence - self.highest_remote_sequence
            if shift <= 32:
                self.ack_bitfield = (self.ack_bitfield << shift) | 1
            else:
                self.ack_bitfield = 1
            self.highest_remote_sequence = sequence
        elif sequence < self.highest_remote_sequence:
            diff = self.highest_remote_sequence - sequence
            if diff <= 32:
                self.ack_bitfield |= (1 << diff)

    def is_packet_acknowledged(self, sequence: int, remote_ack: int, remote_bitfield: int) -> bool:
        """Checks if a sent sequence number was received by remote peer."""
        if sequence == remote_ack:
            return True
        if sequence < remote_ack:
            diff = remote_ack - sequence
            if diff <= 32:
                return bool(remote_bitfield & (1 << diff))
        return False
