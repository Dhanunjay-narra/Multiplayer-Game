"""Dedicated game server allocation and port reservation manager."""
import uuid
import time
from typing import Dict, List, Optional
from shared.schemas.matchmaking_schemas import MatchReservation, ServerAllocationRequest


class ServerAllocator:
    """Allocates dedicated game server instances and reserves ports."""
    def __init__(self, base_port: int = 8000, max_servers: int = 50) -> None:
        self.base_port = base_port
        self.max_servers = max_servers
        self.active_allocations: Dict[str, MatchReservation] = {}
        self._used_ports: set[int] = set()

    def allocate_server(self, req: ServerAllocationRequest) -> MatchReservation:
        """Finds an available server port and creates match reservation."""
        # Find next available port
        allocated_port = None
        for p in range(self.base_port, self.base_port + self.max_servers):
            if p not in self._used_ports:
                allocated_port = p
                self._used_ports.add(p)
                break

        if allocated_port is None:
            allocated_port = self.base_port  # Fallback for dynamic multiplexing

        all_players = req.team_a_players + req.team_b_players
        reservation = MatchReservation(
            match_id=req.match_id,
            map_id=req.map_id,
            server_address="127.0.0.1",
            server_port=allocated_port,
            auth_token=f"mstok_{uuid.uuid4().hex[:16]}",
            assigned_team="Team_A",
            player_ids=all_players,
            expires_at=time.time() + 300.0,
        )
        self.active_allocations[req.match_id] = reservation
        return reservation

    def release_server(self, match_id: str) -> None:
        """Releases the port when match concludes."""
        res = self.active_allocations.pop(match_id, None)
        if res and res.server_port in self._used_ports:
            self._used_ports.remove(res.server_port)

    def get_reservation(self, match_id: str) -> Optional[MatchReservation]:
        return self.active_allocations.get(match_id)


server_allocator = ServerAllocator()
