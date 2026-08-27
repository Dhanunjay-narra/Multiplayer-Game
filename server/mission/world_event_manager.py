"""Reactive dynamic world events and cascading state triggers."""
import uuid
import time
from typing import Dict, List, Optional
from shared.schemas.world_schemas import DynamicWorldEvent


class WorldEventManager:
    """Manages world state transitions and emergency dynamic events."""

    def __init__(self) -> None:
        self.active_events: Dict[str, DynamicWorldEvent] = {}

    def trigger_event(self, event_type: str, territory_id: Optional[str] = None) -> DynamicWorldEvent:
        """Triggers a dynamic event with global game impacts."""
        event_id = f"evt_{uuid.uuid4().hex[:10]}"
        if event_type == "energy_surge":
            title = "Global Nexus Energy Surge"
            desc = "All energy nodes yield 200% harvest rates for the next 5 minutes!"
        elif event_type == "npc_raid":
            title = "Iron Syndicate Assault Wave"
            desc = "Hostile strike teams are attacking player energy nodes. Defend or forfeit territory!"
        else:
            title = "Atmospheric Ion Disruption"
            desc = "Electronic systems degraded. Shield recharge times doubled."

        event = DynamicWorldEvent(
            event_id=event_id,
            title=title,
            description=desc,
            event_type=event_type,
            affected_territory_id=territory_id,
            duration_seconds=300.0,
            is_active=True,
            rewards_multiplier=2.0 if event_type == "energy_surge" else 1.5,
        )
        self.active_events[event_id] = event
        return event

    def get_active_events(self) -> List[DynamicWorldEvent]:
        return [e for e in self.active_events.values() if e.is_active]


world_event_manager = WorldEventManager()
