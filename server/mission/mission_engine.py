"""Data-driven procedural mission engine and dynamic objective evaluator."""
import uuid
from typing import Dict, List, Optional
from shared.enums.game_enums import MissionType, MissionStatus
from shared.schemas.world_schemas import MissionData, MissionObjective


class DynamicMissionEngine:
    """Instantiates, tracks, and evaluates missions across active matches and persistent world."""

    def __init__(self) -> None:
        self.active_missions: Dict[str, MissionData] = {}

    def generate_mission(self, mission_type: MissionType, assigned_player_ids: List[str]) -> MissionData:
        """Procedurally instantiates a structured mission with dynamic objectives."""
        mission_id = f"msn_{uuid.uuid4().hex[:10]}"
        
        if mission_type == MissionType.ENERGY_CAPTURE:
            title = "Secure the Power Grid"
            description = "Infiltrate Sector Alpha and extract 500 units of energy from the active nexus."
            objectives = [
                MissionObjective(objective_id="obj_1", description="Capture Alpha Nexus", target_count=1),
                MissionObjective(objective_id="obj_2", description="Extract 500 Energy Cells", target_count=500),
            ]
            rewards = (600, 350, 150.0)
        elif mission_type == MissionType.SABOTAGE_OUTPOST:
            title = "Sabotage Iron Syndicate Relay"
            description = "Neutralize the defensive relay and eliminate the guarding automated turret."
            objectives = [
                MissionObjective(objective_id="obj_1", description="Sabotage Relay Terminal", target_count=1),
                MissionObjective(objective_id="obj_2", description="Eliminate Patrol Defenders", target_count=3),
            ]
            rewards = (750, 500, 200.0)
        elif mission_type == MissionType.EXTRACTION:
            title = "Priority Resource Extraction"
            description = "Collect high-grade alloy canisters and extract before the ion storm hits."
            objectives = [
                MissionObjective(objective_id="obj_1", description="Collect Alloy Canisters", target_count=4),
                MissionObjective(objective_id="obj_2", description="Reach Evac Extraction Zone", target_count=1),
            ]
            rewards = (1000, 800, 300.0)
        else:
            title = "Territory Reconnaissance"
            description = "Scout hostile perimeter and map the resource distribution."
            objectives = [
                MissionObjective(objective_id="obj_1", description="Scout Strategic Points", target_count=3),
            ]
            rewards = (400, 200, 50.0)

        mission = MissionData(
            mission_id=mission_id,
            title=title,
            description=description,
            mission_type=mission_type,
            status=MissionStatus.IN_PROGRESS,
            assigned_player_ids=assigned_player_ids,
            objectives=objectives,
            time_limit_seconds=600.0,
            reward_xp=rewards[0],
            reward_credits=rewards[1],
            reward_energy=rewards[2],
        )
        self.active_missions[mission_id] = mission
        return mission

    def update_objective_progress(self, mission_id: str, objective_id: str, amount: int = 1) -> bool:
        """Updates objective count and marks completed if all objectives met."""
        mission = self.active_missions.get(mission_id)
        if not mission or mission.status != MissionStatus.IN_PROGRESS:
            return False

        for obj in mission.objectives:
            if obj.objective_id == objective_id and not obj.is_completed:
                obj.current_count = min(obj.target_count, obj.current_count + amount)
                if obj.current_count >= obj.target_count:
                    obj.is_completed = True

        # Check if entire mission is complete
        if all(obj.is_completed for obj in mission.objectives):
            mission.status = MissionStatus.COMPLETED
            return True

        return False

    def get_mission(self, mission_id: str) -> Optional[MissionData]:
        return self.active_missions.get(mission_id)


mission_engine = DynamicMissionEngine()
