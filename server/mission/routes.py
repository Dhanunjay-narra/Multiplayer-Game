"""FastAPI endpoints for missions and dynamic world events."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from server.auth.dependencies import get_current_user
from server.mission.mission_engine import mission_engine
from server.mission.world_event_manager import world_event_manager
from shared.models.db_models import User
from shared.schemas.world_schemas import MissionData, DynamicWorldEvent
from shared.enums.game_enums import MissionType

router = APIRouter(prefix="/api/v1/missions", tags=["Missions & Events"])


@router.post("/request", response_model=MissionData, status_code=status.HTTP_201_CREATED)
async def request_mission(mission_type: MissionType, current_user: User = Depends(get_current_user)):
    """Procedurally generates a mission for the player."""
    return mission_engine.generate_mission(mission_type, [current_user.id])


@router.get("/active", response_model=List[DynamicWorldEvent])
async def get_active_world_events():
    """Returns currently ongoing dynamic world events."""
    return world_event_manager.get_active_events()
