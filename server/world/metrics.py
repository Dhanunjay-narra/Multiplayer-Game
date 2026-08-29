from dataclasses import dataclass, field
from typing import List

@dataclass
class GameServerTelemetry:
    tick_rates: List[float] = field(default_factory=list)
    active_players: int = 0
    total_packets_in: int = 0
    total_packets_out: int = 0

    def record_tick(self, tick_time_ms: float):
        self.tick_rates.append(tick_time_ms)
        if len(self.tick_rates) > 60:
            self.tick_rates.pop(0)

    @property
    def average_tick_ms(self) -> float:
        if not self.tick_rates:
            return 0.0
        return round(sum(self.tick_rates) / len(self.tick_rates), 2)
