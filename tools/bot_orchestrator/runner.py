"""High-concurrency match stress tester and automated bot runner."""
import asyncio
import time
import argparse
from typing import Any, Dict, List
from server.game_server.game_loop import DedicatedGameServer
from client.bot_client.bot_runner import SimulatedBotPlayer
from shared.math.vector import Vector3D
from shared.enums.game_enums import GameState


async def run_simulated_match(num_players: int = 16, duration_seconds: float = 15.0) -> Dict[str, Any]:
    """Runs a dedicated game server with up to 16 concurrent bot players."""
    print(f"=== Starting Nexus Frontier Match Simulation ({num_players} Players) ===")
    server = DedicatedGameServer(match_id="sim_match_001", tick_rate=30)
    server.initialize_world()

    bots: List[SimulatedBotPlayer] = []
    half = num_players // 2
    for i in range(num_players):
        team = "Team_A" if i < half else "Team_B"
        bot = SimulatedBotPlayer(bot_id=f"bot_{i:02d}", name=f"Bot_{i:02d}", team=team)
        server.spawn_player(
            player_id=bot.bot_id,
            username=bot.name,
            team=bot.team,
            character_class=bot.client.character_class,
            spawn_pos=bot.position,
        )
        server.network_manager.register_client(bot.bot_id, bot.name)
        bots.append(bot)

    print(f"Spawned {len(bots)} bot players across Team A and Team B.")
    ticks_to_run = int(duration_seconds * server.tick_rate)
    start_time = time.time()

    for tick_idx in range(ticks_to_run):
        # Gather enemy positions
        team_a_positions = {b.bot_id: b.position for b in bots if b.team == "Team_A"}
        team_b_positions = {b.bot_id: b.position for b in bots if b.team == "Team_B"}

        # Step bot decisions & enqueue input packets
        for bot in bots:
            enemies = team_b_positions if bot.team == "Team_A" else team_a_positions
            packet = bot.step_simulation(server.tick_duration, enemies)
            await server.network_manager.enqueue_packet(packet)

        # Tick dedicated server
        await server.tick(server.tick_duration)

    total_time = time.time() - start_time
    print(f"=== Simulation Complete in {total_time:.2f}s ({server.current_tick} Ticks) ===")
    print(f"Final Scores -> Team A: {server.scores['Team_A']} | Team B: {server.scores['Team_B']}")
    
    return {
        "ticks": server.current_tick,
        "scores": server.scores,
        "match_id": server.match_id,
        "players": len(bots),
    }


def main():
    parser = argparse.ArgumentParser(description="Run multiplayer bot match stress test")
    parser.add_argument("--players", type=int, default=16, help="Number of simulated players (1-16)")
    parser.add_argument("--duration", type=float, default=10.0, help="Simulation duration in seconds")
    args = parser.parse_args()
    asyncio.run(run_simulated_match(num_players=args.players, duration_seconds=args.duration))


if __name__ == "__main__":
    main()
