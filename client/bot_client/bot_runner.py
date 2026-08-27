"""Autonomous headless bot client for match simulation, AI testing, and stress load testing."""
import random
import time
from typing import Dict, Optional
from shared.enums.game_enums import CharacterClass, WeaponType, AbilityType, PacketOpcode
from shared.protocols.packet import GamePacket, PacketHeader
from shared.math.vector import Vector3D
from client.core.game_client import GameClient


class SimulatedBotPlayer:
    """Autonomous simulated bot executing tactical gameplay behaviors in matches."""

    def __init__(self, bot_id: str, name: str, team: str = "Team_A") -> None:
        self.bot_id = bot_id
        self.name = name
        self.team = team
        self.client = GameClient(player_id=bot_id, username=name, team=team)
        self.client.character_class = random.choice(list(CharacterClass))
        self.position = Vector3D(x=-180.0 if team == "Team_A" else 180.0, y=0.0, z=0.0)
        self.target_territory_pos = Vector3D(x=0.0, y=0.0, z=0.0)
        self.is_firing = False
        self.kills = 0
        self.deaths = 0

    def step_simulation(self, delta_time: float, enemy_positions: Dict[str, Vector3D]) -> GamePacket:
        """Generates an authoritative-compatible input packet based on current tactical situation."""
        # 1. Check for nearby enemies
        closest_enemy_id = None
        closest_dist = 999.0
        for eid, epos in enemy_positions.items():
            dist = self.position.distance_to(epos)
            if dist < closest_dist:
                closest_dist = dist
                closest_enemy_id = eid

        move_x = 0.0
        move_z = 0.0
        is_firing = False

        if closest_dist < 40.0 and closest_enemy_id:
            # Engage enemy in combat
            is_firing = True
            dir_to_enemy = (enemy_positions[closest_enemy_id] - self.position).normalized()
            move_x = dir_to_enemy.x * 0.5
            move_z = dir_to_enemy.z * 0.5
        else:
            # Advance towards objective / center nexus
            dir_to_obj = (self.target_territory_pos - self.position).normalized()
            move_x = dir_to_obj.x
            move_z = dir_to_obj.z

        # Create input packet
        p_input = self.client.generate_input(move_x=move_x, move_z=move_z, is_sprinting=True, is_firing=is_firing)
        self.position = self.position + (Vector3D(x=move_x, y=0.0, z=move_z) * (6.0 * 1.6 * delta_time))

        header = PacketHeader(
            opcode=PacketOpcode.PLAYER_INPUT,
            sequence=self.client.input_sequence,
            sender_id=self.bot_id,
        )
        packet = GamePacket(
            header=header,
            payload={
                "input_seq": self.client.input_sequence,
                "move_x": move_x,
                "move_z": move_z,
                "sprint": True,
                "firing": is_firing,
                "target_id": closest_enemy_id if is_firing else None,
            }
        )
        return packet
