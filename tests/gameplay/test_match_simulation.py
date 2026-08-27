"""End-to-end 16-player simulated multiplayer match test."""
import pytest
from tools.bot_orchestrator.runner import run_simulated_match


@pytest.mark.asyncio
async def test_full_16_player_match_simulation():
    """Runs a 16-player match simulation for 120 ticks (4.0s) and validates state progression."""
    result = await run_simulated_match(num_players=16, duration_seconds=4.0)
    assert result["ticks"] == 120
    assert result["players"] == 16
    assert "Team_A" in result["scores"]
    assert "Team_B" in result["scores"]
