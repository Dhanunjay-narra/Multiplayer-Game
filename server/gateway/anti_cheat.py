from dataclasses import dataclass
from typing import Dict
import time

@dataclass
class AntiCheatTracker:
    max_packets_per_sec: int = 120
    max_speed_units_per_sec: float = 25.0

    def __post_init__(self):
        self._packet_counts: Dict[str, int] = {}
        self._last_reset: float = time.time()
        self._last_positions: Dict[str, tuple] = {}

    def validate_packet_rate(self, player_id: str) -> bool:
        now = time.time()
        if now - self._last_reset > 1.0:
            self._packet_counts.clear()
            self._last_reset = now
        count = self._packet_counts.get(player_id, 0) + 1
        self._packet_counts[player_id] = count
        return count <= self.max_packets_per_sec
