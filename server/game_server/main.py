"""Dedicated game server standalone entrypoint."""
import argparse
import asyncio
import logging
from server.game_server.game_loop import DedicatedGameServer
from shared.logging.logger import setup_logger

logger = setup_logger("nexus.game_server")


def parse_args():
    parser = argparse.ArgumentParser(description="Nexus Frontier Dedicated Game Server")
    parser.add_argument("--match-id", type=str, default="match_dev_001", help="Match identifier")
    parser.add_argument("--map-id", type=str, default="frontier_nexus_prime", help="Map identifier")
    parser.add_argument("--port", type=int, default=8765, help="Port to host game server")
    parser.add_argument("--tick-rate", type=int, default=30, help="Simulation tick rate (Hz)")
    return parser.parse_args()


async def main():
    args = parse_args()
    logger.info(f"Launching Dedicated Game Server on port {args.port} [Match: {args.match_id}, Map: {args.map_id}]")
    server = DedicatedGameServer(match_id=args.match_id, map_id=args.map_id, tick_rate=args.tick_rate)
    await server.start()

    try:
        while server._is_running:
            await asyncio.sleep(1.0)
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
