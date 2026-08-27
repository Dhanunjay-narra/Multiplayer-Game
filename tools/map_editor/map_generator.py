"""Procedural map generator for territories, resource nodes, and cover positions."""
import json
import random
from typing import Any, Dict, List
from shared.math.vector import Vector3D
from shared.schemas.world_schemas import TerritoryStateData, EnergyNodeData
from shared.enums.game_enums import FactionType, TerritoryState


class ProceduralMapGenerator:
    """Generates balanced tactical multiplayer maps with mirrored territory objectives."""

    def generate_map(self, map_id: str = "frontier_nexus_prime", map_radius: float = 500.0) -> Dict[str, Any]:
        """Generates symmetrical sectors, energy extractors, and cover nodes."""
        territories = []

        # Central contested Spire
        territories.append({
            "territory_id": "terr_central_spire",
            "name": "Central Ion Spire",
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "radius": 50.0,
            "strategic_value": 300,
            "energy_nodes": [{"node_id": "node_core", "capacity": 3000.0}],
        })

        # Flanking Outposts
        territories.append({
            "territory_id": "terr_alpha_refinery",
            "name": "Alpha Fuel Plant",
            "position": {"x": -map_radius * 0.5, "y": 0.0, "z": 0.0},
            "radius": 40.0,
            "strategic_value": 150,
            "energy_nodes": [{"node_id": "node_alpha", "capacity": 1500.0}],
        })
        territories.append({
            "territory_id": "terr_bravo_relay",
            "name": "Bravo Radar Relay",
            "position": {"x": map_radius * 0.5, "y": 0.0, "z": 0.0},
            "radius": 40.0,
            "strategic_value": 150,
            "energy_nodes": [{"node_id": "node_bravo", "capacity": 1500.0}],
        })

        return {
            "map_id": map_id,
            "radius": map_radius,
            "spawn_points": {
                "Team_A": [{"x": -map_radius * 0.8, "y": 0.0, "z": 0.0}],
                "Team_B": [{"x": map_radius * 0.8, "y": 0.0, "z": 0.0}],
            },
            "territories": territories,
        }


if __name__ == "__main__":
    gen = ProceduralMapGenerator()
    world_map = gen.generate_map()
    print(json.dumps(world_map, indent=2))
