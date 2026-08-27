"""Lobby management service for team composition, map selection, and ready checks."""
import uuid
from typing import Dict, List, Optional
from shared.schemas.lobby_schemas import LobbyCreateRequest, LobbyState, PartyMember
from shared.enums.game_enums import CharacterClass, FactionType


class LobbyService:
    """In-memory and distributed lobby session coordinator."""
    def __init__(self) -> None:
        self._lobbies: Dict[str, LobbyState] = {}
        self._player_to_lobby: Dict[str, str] = {}

    def create_lobby(self, user_id: str, username: str, req: LobbyCreateRequest) -> LobbyState:
        """Creates a new lobby room and sets the creator as leader."""
        # If user is in existing lobby, remove them first
        self.leave_lobby(user_id)

        lobby_id = f"lob_{uuid.uuid4().hex[:10]}"
        leader_member = PartyMember(
            player_id=user_id,
            username=username,
            is_leader=True,
            is_ready=False,
            character_class=CharacterClass.VANGUARD,
            faction=FactionType.SOLARIS_HEGEMONY,
        )

        lobby = LobbyState(
            lobby_id=lobby_id,
            lobby_name=req.lobby_name,
            leader_id=user_id,
            max_players=req.max_players,
            current_players=1,
            selected_map=req.selected_map,
            members=[leader_member],
            teams={"Team_A": [user_id], "Team_B": []},
            is_in_matchmaking=False,
        )
        self._lobbies[lobby_id] = lobby
        self._player_to_lobby[user_id] = lobby_id
        return lobby

    def join_lobby(self, lobby_id: str, user_id: str, username: str) -> LobbyState:
        """Adds a player to an existing lobby and balances teams."""
        self.leave_lobby(user_id)

        if lobby_id not in self._lobbies:
            raise ValueError(f"Lobby {lobby_id} not found")

        lobby = self._lobbies[lobby_id]
        if len(lobby.members) >= lobby.max_players:
            raise ValueError("Lobby is full")

        member = PartyMember(
            player_id=user_id,
            username=username,
            is_leader=False,
            is_ready=False,
        )
        lobby.members.append(member)
        lobby.current_players = len(lobby.members)

        # Team balancing
        team_a = lobby.teams.get("Team_A", [])
        team_b = lobby.teams.get("Team_B", [])
        if len(team_a) <= len(team_b):
            team_a.append(user_id)
        else:
            team_b.append(user_id)
        lobby.teams["Team_A"] = team_a
        lobby.teams["Team_B"] = team_b

        self._player_to_lobby[user_id] = lobby_id
        return lobby

    def leave_lobby(self, user_id: str) -> Optional[str]:
        """Removes a player from their current lobby. Disbands or reassigns leader."""
        lobby_id = self._player_to_lobby.pop(user_id, None)
        if not lobby_id or lobby_id not in self._lobbies:
            return None

        lobby = self._lobbies[lobby_id]
        lobby.members = [m for m in lobby.members if m.player_id != user_id]
        lobby.current_players = len(lobby.members)

        # Remove from teams
        for t in ["Team_A", "Team_B"]:
            if t in lobby.teams and user_id in lobby.teams[t]:
                lobby.teams[t].remove(user_id)

        if not lobby.members:
            # Disband empty lobby
            self._lobbies.pop(lobby_id, None)
        elif lobby.leader_id == user_id:
            # Assign new leader
            lobby.members[0].is_leader = True
            lobby.leader_id = lobby.members[0].player_id

        return lobby_id

    def toggle_ready(self, user_id: str) -> bool:
        """Toggles ready state for a player."""
        lobby_id = self._player_to_lobby.get(user_id)
        if not lobby_id or lobby_id not in self._lobbies:
            raise ValueError("Player is not in a lobby")

        lobby = self._lobbies[lobby_id]
        for m in lobby.members:
            if m.player_id == user_id:
                m.is_ready = not m.is_ready
                return m.is_ready
        return False

    def get_lobby(self, lobby_id: str) -> Optional[LobbyState]:
        return self._lobbies.get(lobby_id)

    def get_player_lobby(self, user_id: str) -> Optional[LobbyState]:
        lobby_id = self._player_to_lobby.get(user_id)
        return self._lobbies.get(lobby_id) if lobby_id else None


lobby_service = LobbyService()
