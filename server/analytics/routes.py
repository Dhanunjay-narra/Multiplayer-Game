"""FastAPI endpoints for telemetry analytics and match replays."""
from fastapi import APIRouter, HTTPException, status
from server.analytics.replay_recorder import replay_recorder, analytics_service, MatchReplay

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & Replays"])


@router.get("/metrics")
async def get_metrics():
    """Returns platform and gameplay telemetry metrics."""
    return analytics_service.get_metrics_summary()


@router.get("/replays/{match_id}", response_model=MatchReplay)
async def get_replay(match_id: str):
    """Retrieves serialized event replay for a finished match."""
    replay = replay_recorder.get_replay(match_id)
    if not replay:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Replay not found")
    return replay
