"""Integration tests for FastAPI Gateway endpoints (Auth, Player, Lobby, Matchmaking, Admin)."""
import pytest
from httpx import AsyncClient, ASGITransport
from server.gateway.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_auth_and_player_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register User
        reg_payload = {
            "username": "tactical_hero",
            "email": "hero@nexusfrontier.com",
            "password": "Password123!",
            "role": "PLAYER",
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        if res_reg.status_code != 201:
            print("REGISTRATION ERROR:", res_reg.json())
        assert res_reg.status_code == 201
        token = res_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get Profile
        res_prof = await client.get("/api/v1/player/profile", headers=headers)
        assert res_prof.status_code == 200
        assert res_prof.json()["username"] == "tactical_hero"

        # 3. Create Character
        char_payload = {
            "character_name": "Ghost_Vanguard",
            "character_class": "VANGUARD",
            "faction": "SOLARIS_HEGEMONY",
        }
        res_char = await client.post("/api/v1/player/character", json=char_payload, headers=headers)
        assert res_char.status_code == 201
        assert res_char.json()["class"] == "VANGUARD"


@pytest.mark.asyncio
async def test_lobby_and_matchmaking_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register user
        reg_payload = {
            "username": "squad_lead",
            "email": "lead@nexusfrontier.com",
            "password": "Password123!",
            "role": "PLAYER",
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        token = res_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create Lobby
        lobby_res = await client.post("/api/v1/lobby/create", json={"lobby_name": "Apex Squad"}, headers=headers)
        assert lobby_res.status_code == 201
        lobby_id = lobby_res.json()["lobby_id"]

        # Toggle Ready
        ready_res = await client.post("/api/v1/lobby/ready", headers=headers)
        assert ready_res.status_code == 200
        assert ready_res.json()["is_ready"] is True

        # Enter Matchmaking Queue
        queue_res = await client.post("/api/v1/matchmaking/queue", headers=headers)
        assert queue_res.status_code == 200
        assert "ticket_id" in queue_res.json()
