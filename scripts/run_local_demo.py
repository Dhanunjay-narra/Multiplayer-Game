"""Local interactive demonstration script for Nexus Frontier."""
import os
import sys
import asyncio
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.game_server.game_loop import DedicatedGameServer
from client.bot_client.bot_runner import SimulatedBotPlayer
from client.ui.terminal_client import TerminalClientUI
from shared.math.vector import Vector3D


async def run_interactive_demo():
    print("=" * 60)
    print("       NEXUS FRONTIER - LIVE MULTIPLAYER DEMO")
    print("=" * 60)

    # 1. Initialize Authoritative Dedicated Server
    server = DedicatedGameServer(match_id="demo_match_alpha", map_id="frontier_nexus_prime", tick_rate=30)
    server.initialize_world()

    # 2. Spawn Human Player
    human_id = "player_hero"
    server.spawn_player(player_id=human_id, username="Commander_Hero", team="Team_A", spawn_pos=Vector3D(x=-180.0, y=0.0, z=0.0))
    server.network_manager.register_client(human_id, "Commander_Hero")

    # 3. Spawn 7 Bot Players (4v4 match)
    bots = []
    for i in range(1, 8):
        team = "Team_A" if i < 4 else "Team_B"
        bot = SimulatedBotPlayer(bot_id=f"bot_{i:02d}", name=f"Operative_{i:02d}", team=team)
        server.spawn_player(bot.bot_id, bot.name, bot.team, bot.client.character_class, bot.position)
        server.network_manager.register_client(bot.bot_id, bot.name)
        bots.append(bot)

    ui = TerminalClientUI(player_id=human_id, username="Commander_Hero")
    print(f"\nSpawned 8 players (4v4 match) on Dedicated Game Server.")
    print("Simulating 60 ticks (2.0s) of active tactical combat...\n")

    for tick in range(60):
        # Step bots
        team_a_pos = {b.bot_id: b.position for b in bots if b.team == "Team_A"}
        team_b_pos = {b.bot_id: b.position for b in bots if b.team == "Team_B"}
        for b in bots:
            enemies = team_b_pos if b.team == "Team_A" else team_a_pos
            packet = b.step_simulation(server.tick_duration, enemies)
            await server.network_manager.enqueue_packet(packet)

        await server.tick(server.tick_duration)

        if tick % 15 == 0:
            snapshot = server.create_snapshot()
            ui.render_hud(snapshot)

    print("\n" + "=" * 60)
    print(f"Match Finished. Final Score: Team A [{server.scores['Team_A']}] - [{server.scores['Team_B']}] Team B")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_interactive_demo())
