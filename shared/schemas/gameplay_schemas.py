"""Real-time gameplay inputs, entity states, snapshot replication, and combat action schemas."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from shared.enums.game_enums import CharacterClass, WeaponType, AbilityType, DamageType
from shared.math.vector import Vector3D


class PlayerInput(BaseModel):
    """Client input sent each tick."""
    input_sequence: int
    client_tick: int
    movement_vector: Vector3D
    view_yaw: float = 0.0
    view_pitch: float = 0.0
    is_sprinting: bool = False
    is_crouching: bool = False
    is_jumping: bool = False
    is_firing: bool = False
    is_reloading: bool = False
    active_weapon_slot: int = 0
    activated_ability: Optional[AbilityType] = None


class EntityTransform(BaseModel):
    position: Vector3D
    velocity: Vector3D
    rotation_yaw: float = 0.0
    rotation_pitch: float = 0.0


class PlayerCombatState(BaseModel):
    health: float = 100.0
    max_health: float = 100.0
    shield: float = 100.0
    max_shield: float = 100.0
    stamina: float = 100.0
    is_alive: bool = True
    is_knocked: bool = False
    is_shield_broken: bool = False
    active_weapon: WeaponType = WeaponType.ASSAULT_RIFLE
    ammo_in_clip: int = 30
    reserve_ammo: int = 180
    primary_ability_cooldown: float = 0.0
    secondary_ability_cooldown: float = 0.0


class PlayerSnapshot(BaseModel):
    player_id: str
    username: str
    team: str
    character_class: CharacterClass
    transform: EntityTransform
    combat_state: PlayerCombatState
    ping_ms: int = 20


class ProjectileSnapshot(BaseModel):
    projectile_id: str
    owner_id: str
    damage_type: DamageType
    damage: float
    position: Vector3D
    velocity: Vector3D
    lifespan_remaining: float


class GameStateSnapshot(BaseModel):
    """Full authoritative state broadcast from dedicated server."""
    server_tick: int
    server_time: float
    players: Dict[str, PlayerSnapshot] = Field(default_factory=dict)
    projectiles: List[ProjectileSnapshot] = Field(default_factory=list)
    scores: Dict[str, int] = Field(default_factory=dict)
    match_time_remaining: float = 600.0


class DeltaSnapshot(BaseModel):
    """Delta-compressed snapshot containing only mutated entities."""
    server_tick: int
    reference_tick: int
    updated_players: Dict[str, PlayerSnapshot] = Field(default_factory=dict)
    removed_player_ids: List[str] = Field(default_factory=list)
    projectiles: List[ProjectileSnapshot] = Field(default_factory=list)
    scores: Dict[str, int] = Field(default_factory=dict)


class CombatActionRequest(BaseModel):
    action_type: str  # "fire", "reload", "melee"
    origin: Vector3D
    direction: Vector3D
    weapon_type: WeaponType
    timestamp_ms: float


class HitConfirmation(BaseModel):
    shooter_id: str
    target_id: str
    hit_location: str  # "head", "body", "limb"
    damage_dealt: float
    shield_absorbed: float
    target_remaining_health: float
    target_killed: bool
    critical_hit: bool
