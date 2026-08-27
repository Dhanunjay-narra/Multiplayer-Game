"""Dynamic world, territory, weather, and world event schemas."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from shared.enums.game_enums import FactionType, TerritoryState, WeatherType, MissionType, MissionStatus
from shared.math.vector import Vector3D


class EnergyNodeData(BaseModel):
    node_id: str
    position: Vector3D
    max_energy_capacity: float = 1000.0
    current_energy: float = 1000.0
    is_extracting: bool = False
    controlling_faction: FactionType = FactionType.NEUTRAL


class TerritoryStateData(BaseModel):
    territory_id: str
    name: str
    controlling_faction: FactionType = FactionType.NEUTRAL
    state: TerritoryState = TerritoryState.UNCONTESTED
    defense_level: int = 1
    capture_progress: float = 0.0  # 0.0 to 100.0%
    capturing_team: Optional[str] = None
    center_position: Vector3D
    radius: float = 50.0
    nodes: List[EnergyNodeData] = Field(default_factory=list)
    strategic_value: int = 100


class WeatherState(BaseModel):
    weather_type: WeatherType = WeatherType.CLEAR
    intensity: float = 0.0  # 0.0 to 1.0
    duration_remaining_seconds: float = 300.0
    visibility_multiplier: float = 1.0
    shield_regen_blocked: bool = False


class DynamicWorldEvent(BaseModel):
    event_id: str
    title: str
    description: str
    event_type: str  # "energy_surge", "npc_raid", "ion_storm", "resource_shortage"
    affected_territory_id: Optional[str] = None
    duration_seconds: float = 180.0
    is_active: bool = True
    rewards_multiplier: float = 1.5


class MissionObjective(BaseModel):
    objective_id: str
    description: str
    target_count: int = 1
    current_count: int = 0
    is_completed: bool = False


class MissionData(BaseModel):
    mission_id: str
    title: str
    description: str
    mission_type: MissionType
    status: MissionStatus = MissionStatus.AVAILABLE
    assigned_player_ids: List[str] = Field(default_factory=list)
    objectives: List[MissionObjective] = Field(default_factory=list)
    time_limit_seconds: float = 600.0
    time_elapsed_seconds: float = 0.0
    reward_xp: int = 500
    reward_credits: int = 250
    reward_energy: float = 100.0
