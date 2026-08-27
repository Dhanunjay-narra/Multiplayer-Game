"""Client networking, prediction, reconciliation, and state interpolation engine."""
import asyncio
import time
from typing import Any, Dict, List, Optional
from shared.enums.game_enums import PacketOpcode, CharacterClass, WeaponType, AbilityType
from shared.protocols.packet import GamePacket, PacketHeader, SequenceTracker
from shared.schemas.gameplay_schemas import PlayerInput, GameStateSnapshot, PlayerSnapshot
from shared.math.vector import Vector3D


class GameClient:
    """Core game client managing network synchronization and local prediction."""

    def __init__(self, player_id: str, username: str, team: str = "Team_A") -> None:
        self.player_id = player_id
        self.username = username
        self.team = team
        self.character_class = CharacterClass.VANGUARD
        self.sequence_tracker = SequenceTracker()
        self.input_sequence = 0
        self.predicted_position = Vector3D.zero()
        self.predicted_velocity = Vector3D.zero()
        self.pending_inputs: List[PlayerInput] = []
        self.latest_snapshot: Optional[GameStateSnapshot] = None
        self.is_connected = False

    def generate_input(
        self,
        move_x: float,
        move_z: float,
        is_sprinting: bool = False,
        is_firing: bool = False,
        activated_ability: Optional[AbilityType] = None,
    ) -> PlayerInput:
        """Constructs and stores a predicted input packet."""
        self.input_sequence += 1
        p_input = PlayerInput(
            input_sequence=self.input_sequence,
            client_tick=self.input_sequence,
            movement_vector=Vector3D(x=move_x, y=0.0, z=move_z),
            is_sprinting=is_sprinting,
            is_firing=is_firing,
            activated_ability=activated_ability,
        )
        self.pending_inputs.append(p_input)
        return p_input

    def reconcile_state(self, server_snapshot: GameStateSnapshot) -> None:
        """Server reconciliation: reconciles predicted position against authoritative snapshot."""
        self.latest_snapshot = server_snapshot
        my_snap = server_snapshot.players.get(self.player_id)
        if not my_snap:
            return

        auth_pos = my_snap.transform.position
        # Discard acknowledged inputs
        self.pending_inputs = [inp for inp in self.pending_inputs if inp.input_sequence > my_snap.combat_state.ammo_in_clip]
        self.predicted_position = auth_pos
