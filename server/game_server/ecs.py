"""Entity Component System (ECS) architecture for high-performance authoritative simulation."""
from __future__ import annotations
import time
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel, Field
from shared.enums.game_enums import CharacterClass, WeaponType, AbilityType, FactionType, TerritoryState
from shared.math.vector import Vector3D

T = TypeVar("T")


class Component:
    """Base marker class for ECS components."""
    pass


class TransformComponent(Component):
    def __init__(self, position: Optional[Vector3D] = None, velocity: Optional[Vector3D] = None) -> None:
        self.position: Vector3D = position or Vector3D.zero()
        self.velocity: Vector3D = velocity or Vector3D.zero()
        self.yaw: float = 0.0
        self.pitch: float = 0.0


class HealthComponent(Component):
    def __init__(self, max_health: float = 100.0, max_shield: float = 100.0) -> None:
        self.max_health: float = max_health
        self.health: float = max_health
        self.max_shield: float = max_shield
        self.shield: float = max_shield
        self.is_alive: bool = True
        self.is_knocked: bool = False
        self.last_damage_time: float = 0.0
        self.respawn_timer: float = 0.0


class WeaponComponent(Component):
    def __init__(
        self,
        primary_weapon: WeaponType = WeaponType.ASSAULT_RIFLE,
        secondary_weapon: WeaponType = WeaponType.TACTICAL_PISTOL,
    ) -> None:
        self.primary_weapon: WeaponType = primary_weapon
        self.secondary_weapon: WeaponType = secondary_weapon
        self.active_slot: int = 0
        self.ammo_in_clip: int = 30
        self.reserve_ammo: int = 180
        self.fire_cooldown_remaining: float = 0.0
        self.is_reloading: bool = False
        self.reload_timer: float = 0.0
        self.last_fire_time: float = 0.0


class AbilityComponent(Component):
    def __init__(
        self,
        primary_ability: AbilityType = AbilityType.SHIELD_DOME,
        secondary_ability: AbilityType = AbilityType.RECON_RADAR,
    ) -> None:
        self.primary_ability: AbilityType = primary_ability
        self.secondary_ability: AbilityType = secondary_ability
        self.primary_cooldown: float = 0.0
        self.secondary_cooldown: float = 0.0
        self.active_buff_duration: float = 0.0
        self.is_cloaked: bool = False


class PlayerComponent(Component):
    def __init__(
        self,
        player_id: str,
        username: str,
        team: str = "Team_A",
        character_class: CharacterClass = CharacterClass.VANGUARD,
    ) -> None:
        self.player_id: str = player_id
        self.username: str = username
        self.team: str = team
        self.character_class: CharacterClass = character_class
        self.kills: int = 0
        self.deaths: int = 0
        self.assists: int = 0
        self.damage_dealt: float = 0.0
        self.last_input_sequence: int = 0
        self.ping_ms: int = 20


class TerritoryNodeComponent(Component):
    def __init__(self, territory_id: str, name: str, position: Vector3D, radius: float = 35.0) -> None:
        self.territory_id: str = territory_id
        self.name: str = name
        self.position: Vector3D = position
        self.radius: float = radius
        self.owner_faction: FactionType = FactionType.NEUTRAL
        self.state: TerritoryState = TerritoryState.UNCONTESTED
        self.capture_progress: float = 0.0
        self.defense_level: int = 1
        self.energy_stored: float = 500.0


class AIControllerComponent(Component):
    def __init__(self, faction: FactionType = FactionType.IRON_SYNDICATE, patrol_radius: float = 100.0) -> None:
        self.faction: FactionType = faction
        self.current_state: str = "PATROL"  # "PATROL", "CHASE", "ATTACK", "COVER", "DEFEND"
        self.target_entity_id: Optional[str] = None
        self.patrol_origin: Vector3D = Vector3D.zero()
        self.patrol_radius: float = patrol_radius
        self.patrol_target: Vector3D = Vector3D.zero()
        self.aggro_range: float = 60.0
        self.attack_range: float = 40.0
        self.last_decision_time: float = 0.0


class Entity:
    """Game simulation entity holding components."""
    def __init__(self, entity_id: str, entity_type: str = "player") -> None:
        self.id: str = entity_id
        self.entity_type: str = entity_type
        self.is_active: bool = True
        self.components: Dict[Type[Component], Component] = {}

    def add_component(self, component: Component) -> Entity:
        self.components[type(component)] = component
        return self

    def get_component(self, component_cls: Type[T]) -> Optional[T]:
        return self.components.get(component_cls)  # type: ignore

    def has_component(self, component_cls: Type[Component]) -> bool:
        return component_cls in self.components

    def remove_component(self, component_cls: Type[Component]) -> None:
        self.components.pop(component_cls, None)


class EntityManager:
    """Manages creation, querying, and destruction of all world entities."""
    def __init__(self) -> None:
        self._entities: Dict[str, Entity] = {}

    def create_entity(self, entity_id: str, entity_type: str = "player") -> Entity:
        entity = Entity(entity_id=entity_id, entity_type=entity_type)
        self._entities[entity_id] = entity
        return entity

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self._entities.get(entity_id)

    def remove_entity(self, entity_id: str) -> None:
        self._entities.pop(entity_id, None)

    def get_all_entities(self) -> List[Entity]:
        return list(self._entities.values())

    def get_entities_with(self, *component_types: Type[Component]) -> List[Entity]:
        """Returns all entities that have all requested components."""
        return [
            e for e in self._entities.values()
            if e.is_active and all(e.has_component(c) for c in component_types)
        ]

    def clear(self) -> None:
        self._entities.clear()
