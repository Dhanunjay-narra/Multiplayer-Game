"""Dynamic world engine managing weather patterns, day/night cycles, and territory grids."""
import time
import random
from typing import Dict, List, Optional
from shared.enums.game_enums import WeatherType, TerritoryState, FactionType
from shared.schemas.world_schemas import WeatherState, TerritoryStateData, EnergyNodeData
from shared.math.vector import Vector3D


class DynamicWorldEngine:
    """Simulates living world conditions, environmental hazards, and strategic nodes."""

    def __init__(self, map_id: str = "frontier_nexus_prime") -> None:
        self.map_id: str = map_id
        self.time_of_day: float = 12.0  # 0.0 to 24.0 hours
        self.weather_state: WeatherState = WeatherState(
            weather_type=WeatherType.CLEAR,
            intensity=0.0,
            duration_remaining_seconds=300.0,
            visibility_multiplier=1.0,
            shield_regen_blocked=False,
        )
        self.territories: Dict[str, TerritoryStateData] = {}
        self._init_default_territories()

    def _init_default_territories(self) -> None:
        """Initializes default strategic sectors and energy extraction nodes."""
        self.territories["terr_alpha"] = TerritoryStateData(
            territory_id="terr_alpha",
            name="Alpha Refinery Sector",
            controlling_faction=FactionType.NEUTRAL,
            state=TerritoryState.UNCONTESTED,
            defense_level=1,
            center_position=Vector3D(x=-250.0, y=0.0, z=0.0),
            radius=40.0,
            strategic_value=150,
            nodes=[
                EnergyNodeData(node_id="node_a1", position=Vector3D(x=-250.0, y=0.0, z=0.0), current_energy=1000.0)
            ],
        )
        self.territories["terr_bravo"] = TerritoryStateData(
            territory_id="terr_bravo",
            name="Bravo Communications Relay",
            controlling_faction=FactionType.NEUTRAL,
            state=TerritoryState.UNCONTESTED,
            defense_level=1,
            center_position=Vector3D(x=250.0, y=0.0, z=0.0),
            radius=40.0,
            strategic_value=120,
            nodes=[
                EnergyNodeData(node_id="node_b1", position=Vector3D(x=250.0, y=0.0, z=0.0), current_energy=1000.0)
            ],
        )
        self.territories["terr_central_nexus"] = TerritoryStateData(
            territory_id="terr_central_nexus",
            name="Central Core Spire",
            controlling_faction=FactionType.NEUTRAL,
            state=TerritoryState.UNCONTESTED,
            defense_level=2,
            center_position=Vector3D(x=0.0, y=0.0, z=150.0),
            radius=55.0,
            strategic_value=300,
            nodes=[
                EnergyNodeData(node_id="node_c1", position=Vector3D(x=0.0, y=0.0, z=150.0), current_energy=2500.0)
            ],
        )

    def update(self, delta_time: float) -> None:
        """Advances day/night cycle, weather duration, and resource extraction."""
        # Advance 24h clock (1 real minute = 1 in-game hour)
        self.time_of_day = (self.time_of_day + (delta_time / 60.0)) % 24.0

        # Weather cycle
        self.weather_state.duration_remaining_seconds -= delta_time
        if self.weather_state.duration_remaining_seconds <= 0:
            self._transition_weather()

        # Extract energy from controlled territories
        for terr in self.territories.values():
            if terr.controlling_faction != FactionType.NEUTRAL:
                for node in terr.nodes:
                    if node.current_energy > 0:
                        extracted = min(node.current_energy, delta_time * 5.0 * terr.defense_level)
                        node.current_energy -= extracted

    def _transition_weather(self) -> None:
        """Transitions between weather patterns."""
        choices = [WeatherType.CLEAR, WeatherType.SANDSTORM, WeatherType.ION_STORM, WeatherType.CORROSIVE_RAIN]
        new_weather = random.choice(choices)
        duration = random.uniform(180.0, 360.0)

        if new_weather == WeatherType.SANDSTORM:
            self.weather_state = WeatherState(
                weather_type=WeatherType.SANDSTORM,
                intensity=0.8,
                duration_remaining_seconds=duration,
                visibility_multiplier=0.5,
                shield_regen_blocked=False,
            )
        elif new_weather == WeatherType.ION_STORM:
            self.weather_state = WeatherState(
                weather_type=WeatherType.ION_STORM,
                intensity=1.0,
                duration_remaining_seconds=duration,
                visibility_multiplier=0.8,
                shield_regen_blocked=True,
            )
        else:
            self.weather_state = WeatherState(
                weather_type=WeatherType.CLEAR,
                intensity=0.0,
                duration_remaining_seconds=duration,
                visibility_multiplier=1.0,
                shield_regen_blocked=False,
            )
