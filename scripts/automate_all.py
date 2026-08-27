"""Master Automation Script: Executes the entire Nexus Frontier platform lifecycle end-to-end.

Workflow:
1. Initializes SQLite/PostgreSQL Database
2. Registers 8 Players (4v4 Teams) & Creates Tactical Loadouts
3. Allocates Initial Wallets (Credits, Energy, Alloy) & Default Gear
4. Forms Lobbies & Queues Matchmaking Tickets
5. Starts Authoritative Dedicated Game Server (30 Hz Tick Loop)
6. Connects all 8 Players and Simulates 120 Ticks (Combat, Abilities, Territory Captures)
7. Triggers Dynamic World Events & Completes Mission Objectives
8. Concludes Match, Awards XP/Credits, and Persists Results to DB
"""

import os
import sys
import asyncio
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.database import init_db, async_session_factory
from server.auth.auth_service import auth_service
from server.player.player_service import player_service
from server.lobby.lobby_service import lobby_service
from server.matchmaking.matchmaker import matchmaker
from server.matchmaking.server_allocator import server_allocator
from server.game_server.game_loop import DedicatedGameServer
from server.inventory.inventory_service import inventory_service
from server.economy.wallet_service import wallet_service
from server.mission.mission_engine import mission_engine
from server.mission.world_event_manager import world_event_manager
from client.bot_client.bot_runner import SimulatedBotPlayer
from shared.schemas.auth_schemas import RegisterRequest
from shared.schemas.player_schemas import CharacterCreateRequest
from shared.schemas.lobby_schemas import LobbyCreateRequest
from shared.enums.game_enums import CharacterClass, FactionType, MissionType, CurrencyType
from shared.math.vector import Vector3D


async def run_full_autonomous_lifecycle():
    print("=" * 70)
    print("      NEXUS FRONTIER: FULL AUTONOMOUS PLATFORM LIFECYCLE")
    print("=" * 70)

    # Step 1: Database Initialization
    print("\n[Step 1/8] Initializing Database Schema...")
    await init_db()
    print("  -> Database schema initialized successfully.")

    # Step 2: Automated Player Accounts & Loadout Creation
    print("\n[Step 2/8] Registering 8 Tactical Players...")
    created_players = []
    classes = [
        CharacterClass.VANGUARD,
        CharacterClass.INFILTRATOR,
        CharacterClass.TECH_ENGINEER,
        CharacterClass.NANO_MEDIC,
    ]

    async with async_session_factory() as session:
        for i in range(8):
            username = f"Operative_{i+1:02d}"
            email = f"operative_{i+1:02d}@nexusfrontier.com"
            char_class = classes[i % len(classes)]
            faction = FactionType.SOLARIS_HEGEMONY if i < 4 else FactionType.IRON_SYNDICATE

            # Register User
            user = await auth_service.register_user(
                session,
                RegisterRequest(username=username, email=email, password="Password123!")
            )

            # Create Character
            char = await player_service.create_character(
                session,
                user.id,
                CharacterCreateRequest(
                    character_name=f"Char_{username}",
                    character_class=char_class,
                    faction=faction,
                )
            )

            created_players.append({
                "user_id": user.id,
                "username": username,
                "class": char_class,
                "faction": faction,
                "team": "Team_A" if i < 4 else "Team_B",
            })
            print(f"  -> Created: {username} | Class: {char_class.value} | Faction: {faction.value} | Team: {'Team_A' if i < 4 else 'Team_B'}")

    # Step 3: Verify Initial Inventory & Wallet Ledger
    print("\n[Step 3/8] Verifying Player Economy & Starting Gear...")
    for p in created_players[:2]:
        inv = inventory_service.get_or_create_inventory(p["user_id"])
        wal = wallet_service.get_or_create_wallet(p["user_id"])
        print(f"  -> {p['username']}: Inventory Slots Filled: {len([s for s in inv.slots.values() if s is not None])}/24 | Credits: {wal.balances[CurrencyType.CREDITS]}")

    # Step 4: Automated Lobby & Matchmaking
    print("\n[Step 4/8] Executing Lobby Formation & Matchmaking...")
    leader = created_players[0]
    lobby = lobby_service.create_lobby(
        leader["user_id"],
        leader["username"],
        LobbyCreateRequest(lobby_name="Operation Frontier Breach", max_players=8)
    )
    for p in created_players[1:]:
        lobby_service.join_lobby(lobby.lobby_id, p["user_id"], p["username"])
        lobby_service.toggle_ready(p["user_id"])
    lobby_service.toggle_ready(leader["user_id"])
    print(f"  -> Lobby {lobby.lobby_id} formed with {len(lobby.members)} ready players.")

    # Step 5: Dedicated Game Server Launch
    print("\n[Step 5/8] Launching Dedicated Authoritative Game Server (30 Hz)...")
    match_id = f"match_auto_{int(time.time())}"
    game_server = DedicatedGameServer(match_id=match_id, map_id="frontier_nexus_prime", tick_rate=30)
    game_server.initialize_world()

    bots = []
    for p in created_players:
        bot = SimulatedBotPlayer(bot_id=p["user_id"], name=p["username"], team=p["team"])
        bot.client.character_class = p["class"]
        game_server.spawn_player(
            player_id=bot.bot_id,
            username=bot.name,
            team=bot.team,
            character_class=bot.client.character_class,
            spawn_pos=bot.position,
        )
        game_server.network_manager.register_client(bot.bot_id, bot.name)
        bots.append(bot)
    print(f"  -> Dedicated Server ready with {len(bots)} active tactical combatants.")

    # Step 6: Trigger Dynamic Mission & World Event
    print("\n[Step 6/8] Generating Dynamic World Mission & Event...")
    mission = mission_engine.generate_mission(
        MissionType.ENERGY_CAPTURE, [p["user_id"] for p in created_players[:4]]
    )
    event = world_event_manager.trigger_event("energy_surge", territory_id="terr_alpha")
    print(f"  -> Active Mission: '{mission.title}' (Reward: {mission.reward_xp} XP, {mission.reward_credits} Credits)")
    print(f"  -> World Event: '{event.title}' - {event.description}")

    # Step 7: Authoritative 120-Tick Simulation Loop
    print("\n[Step 7/8] Simulating Authoritative Match (120 Ticks / 4.0 Seconds)...")
    for tick in range(120):
        team_a_pos = {b.bot_id: b.position for b in bots if b.team == "Team_A"}
        team_b_pos = {b.bot_id: b.position for b in bots if b.team == "Team_B"}

        for b in bots:
            enemies = team_b_pos if b.team == "Team_A" else team_a_pos
            packet = b.step_simulation(game_server.tick_duration, enemies)
            await game_server.network_manager.enqueue_packet(packet)

        await game_server.tick(game_server.tick_duration)

        # Progress mission during match
        if tick == 60:
            mission_engine.update_objective_progress(mission.mission_id, "obj_1", 1)
            mission_engine.update_objective_progress(mission.mission_id, "obj_2", 500)

    print(f"  -> Simulation complete: {game_server.current_tick} ticks processed.")
    print(f"  -> Mission Status: {mission.status.value}")
    print(f"  -> Match Scores: Team A [{game_server.scores['Team_A']}] - [{game_server.scores['Team_B']}] Team B")

    # Step 8: Match Resolution, Rewards & Database Persistence
    print("\n[Step 8/8] Resolving Match Results & Persisting Rewards...")
    async with async_session_factory() as session:
        for p in created_players:
            # Grant XP and Credits for match completion
            leveled_up = await player_service.add_xp(session, p["user_id"], xp_amount=1200)
            wallet_service.modify_balance(
                p["user_id"],
                CurrencyType.CREDITS,
                amount=500.0,
                description=f"Match {match_id} Reward"
            )
            prof = await player_service.get_player_profile(session, p["user_id"])
            wal = wallet_service.get_or_create_wallet(p["user_id"])
            print(f"  -> {p['username']}: Level {prof.level} (XP: {prof.current_xp}/{prof.next_level_xp}) | Credits: {wal.balances[CurrencyType.CREDITS]} (Leveled Up: {leveled_up})")

    print("\n" + "=" * 70)
    print("      ALL PLATFORM LIFECYCLE STAGES COMPLETED AUTOMATICALLY")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_full_autonomous_lifecycle())
