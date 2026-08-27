"""Skill-based, latency-aware matchmaking queue manager."""
import uuid
import time
import math
from typing import Dict, List, Optional
from shared.schemas.matchmaking_schemas import MatchmakingTicket, MatchReservation, ServerAllocationRequest
from shared.enums.game_enums import RankTier
from server.matchmaking.server_allocator import server_allocator


class MatchmakingQueue:
    """MMR and Region-based matchmaking engine."""
    def __init__(self, target_players_per_match: int = 4) -> None:
        self.target_players = target_players_per_match
        self.tickets: Dict[str, MatchmakingTicket] = {}
        self.player_to_ticket: Dict[str, str] = {}
        self.matches: Dict[str, MatchReservation] = {}

    def enqueue_player(
        self,
        player_id: str,
        username: str,
        mmr: int = 1200,
        rank_tier: RankTier = RankTier.UNRANKED,
        region: str = "us-east",
    ) -> MatchmakingTicket:
        """Enqueues a player and checks for immediate match formation."""
        # Cancel any previous ticket
        self.dequeue_player(player_id)

        ticket_id = f"tkt_{uuid.uuid4().hex[:10]}"
        ticket = MatchmakingTicket(
            ticket_id=ticket_id,
            player_id=player_id,
            username=username,
            rank_tier=rank_tier,
            mmr=mmr,
            region=region,
            created_at=time.time(),
            matched=False,
        )
        self.tickets[ticket_id] = ticket
        self.player_to_ticket[player_id] = ticket_id

        # Attempt matchmaking pass
        self.process_queue()
        return ticket

    def dequeue_player(self, player_id: str) -> Optional[str]:
        """Removes a player from the queue."""
        ticket_id = self.player_to_ticket.pop(player_id, None)
        if ticket_id and ticket_id in self.tickets:
            self.tickets.pop(ticket_id, None)
            return ticket_id
        return None

    def get_ticket_status(self, ticket_id: str) -> Optional[MatchmakingTicket]:
        return self.tickets.get(ticket_id)

    def process_queue(self) -> Optional[MatchReservation]:
        """Evaluates active tickets and forms balanced matches."""
        unmatched_tickets = [t for t in self.tickets.values() if not t.matched]
        if len(unmatched_tickets) < self.target_players:
            return None

        # Group by region
        by_region: Dict[str, List[MatchmakingTicket]] = {}
        for t in unmatched_tickets:
            by_region.setdefault(t.region, []).append(t)

        for region, region_tickets in by_region.items():
            if len(region_tickets) >= self.target_players:
                # Sort by MMR
                sorted_tickets = sorted(region_tickets, key=lambda t: t.mmr)
                match_group = sorted_tickets[:self.target_players]

                # Balance into Team A and Team B (snake draft)
                team_a: List[str] = []
                team_b: List[str] = []
                for i, t in enumerate(match_group):
                    if i % 2 == 0:
                        team_a.append(t.player_id)
                    else:
                        team_b.append(t.player_id)

                match_id = f"mat_{uuid.uuid4().hex[:10]}"
                req = ServerAllocationRequest(
                    match_id=match_id,
                    map_id="frontier_nexus_prime",
                    team_a_players=team_a,
                    team_b_players=team_b,
                    region=region,
                )
                reservation = server_allocator.allocate_server(req)
                self.matches[match_id] = reservation

                # Mark tickets matched
                for t in match_group:
                    t.matched = True
                    t.match_id = match_id

                return reservation

        return None


matchmaker = MatchmakingQueue(target_players_per_match=4)
