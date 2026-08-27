"""Enumerations used across Nexus Frontier game systems."""
from enum import Enum, auto


class GameState(str, Enum):
    """Lifecycle states for matches and dedicated servers."""
    INITIALIZING = "INITIALIZING"
    WAITING_FOR_PLAYERS = "WAITING_FOR_PLAYERS"
    WARMUP = "WARMUP"
    COUNTDOWN = "COUNTDOWN"
    ACTIVE = "ACTIVE"
    OVERTIME = "OVERTIME"
    COMPLETED = "COMPLETED"
    SHUTTING_DOWN = "SHUTTING_DOWN"


class CharacterClass(str, Enum):
    """Playable character tactical classes."""
    VANGUARD = "VANGUARD"      # Frontline tank, heavy shields, fortifications
    INFILTRATOR = "INFILTRATOR"  # Stealth, high mobility, recon radar, sniper
    TECH_ENGINEER = "TECH_ENGINEER" # Drone deployment, turret repair, energy node boosts
    NANO_MEDIC = "NANO_MEDIC"  # Area healing, revival stims, combat buffs
    STORM_OPERATIVE = "STORM_OPERATIVE" # Heavy ordnance, EMP strikes, suppression


class FactionType(str, Enum):
    """Persistent world and match factions."""
    SOLARIS_HEGEMONY = "SOLARIS_HEGEMONY"  # High tech, energy shields, authoritarian
    IRON_SYNDICATE = "IRON_SYNDICATE"      # Heavy industrial, ballistic weapons, ruthless
    CYBER_NEXUS = "CYBER_NEXUS"            # AI-hybrid, electronic warfare, drones
    VOID_OUTCASTS = "VOID_OUTCASTS"        # Guerrilla, scavengers, bio-enhancements
    NEUTRAL = "NEUTRAL"                    # Unaligned settlements, mercenary stations


class FactionRelation(str, Enum):
    """Diplomatic relationship between factions."""
    ALLIED = "ALLIED"
    FRIENDLY = "FRIENDLY"
    NEUTRAL = "NEUTRAL"
    HOSTILE = "HOSTILE"
    AT_WAR = "AT_WAR"


class WeaponType(str, Enum):
    """Data-driven weapon classifications."""
    ASSAULT_RIFLE = "ASSAULT_RIFLE"
    PLASMA_SNIPER = "PLASMA_SNIPER"
    SCATTER_SHOTGUN = "SCATTER_SHOTGUN"
    ARC_CANNON = "ARC_CANNON"
    HEAVY_MG = "HEAVY_MG"
    TACTICAL_PISTOL = "TACTICAL_PISTOL"
    ENERGY_BLADE = "ENERGY_BLADE"


class DamageType(str, Enum):
    """Types of damage mitigated by different armor/shield types."""
    KINETIC = "KINETIC"
    ENERGY = "ENERGY"
    EXPLOSIVE = "EXPLOSIVE"
    EMP = "EMP"
    CORROSIVE = "CORROSIVE"
    TRUE_DAMAGE = "TRUE_DAMAGE"


class AbilityType(str, Enum):
    """Character tactical abilities."""
    SHIELD_DOME = "SHIELD_DOME"
    RECON_RADAR = "RECON_RADAR"
    EMP_BURST = "EMP_BURST"
    TELEPORT_BEACON = "TELEPORT_BEACON"
    NANO_HEAL_FIELD = "NANO_HEAL_FIELD"
    ATTACK_DRONE = "ATTACK_DRONE"
    CLOAKING = "CLOAKING"
    FORTIFY_NODE = "FORTIFY_NODE"


class TerritoryState(str, Enum):
    """Territory control states."""
    UNCONTESTED = "UNCONTESTED"
    CONTESTED = "CONTESTED"
    FORTIFIED = "FORTIFIED"
    VULNERABLE = "VULNERABLE"
    OVERCHARGED = "OVERCHARGED"
    DEPLETED = "DEPLETED"


class WeatherType(str, Enum):
    """Dynamic world weather conditions affecting visibility and shields."""
    CLEAR = "CLEAR"
    SANDSTORM = "SANDSTORM"       # Reduces vision range by 50%
    ION_STORM = "ION_STORM"       # Disables shield regeneration, interferes with radar
    CORROSIVE_RAIN = "CORROSIVE_RAIN" # Slow armor degradation over time
    NIGHT = "NIGHT"               # Low light, requires thermal / night-vision


class MissionType(str, Enum):
    """Data-driven mission archetypes."""
    EXPLORATION = "EXPLORATION"
    ENERGY_CAPTURE = "ENERGY_CAPTURE"
    ESCORT_CONVOY = "ESCORT_CONVOY"
    BASE_DEFENSE = "BASE_DEFENSE"
    SABOTAGE_OUTPOST = "SABOTAGE_OUTPOST"
    ASSASSINATION = "ASSASSINATION"
    EXTRACTION = "EXTRACTION"
    SURVIVAL_WAVE = "SURVIVAL_WAVE"


class MissionStatus(str, Enum):
    """Mission lifecycle states."""
    AVAILABLE = "AVAILABLE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class ItemRarity(str, Enum):
    """Rarity levels for inventory items, weapons, and components."""
    COMMON = "COMMON"
    UNCOMMON = "UNCOMMON"
    RARE = "RARE"
    EPIC = "EPIC"
    LEGENDARY = "LEGENDARY"
    EXOTIC = "EXOTIC"


class ItemCategory(str, Enum):
    """Broad inventory categories."""
    WEAPON = "WEAPON"
    ARMOR = "ARMOR"
    ABILITY_MODULE = "ABILITY_MODULE"
    RESOURCE = "RESOURCE"
    CONSUMABLE = "CONSUMABLE"
    BLUEPRINT = "BLUEPRINT"
    COSMETIC = "COSMETIC"
    QUEST_ITEM = "QUEST_ITEM"


class CurrencyType(str, Enum):
    """Economic currencies."""
    CREDITS = "CREDITS"              # Standard transaction currency
    ENERGY_CELLS = "ENERGY_CELLS"    # Upgrades, territory fortifications
    ALLOY_MATERIALS = "ALLOY_MATERIALS" # Crafting weapons & armor
    FACTION_TOKENS = "FACTION_TOKENS" # Exclusive faction equipment
    SEASON_TOKENS = "SEASON_TOKENS"  # Battle pass & cosmetic rewards


class RankTier(str, Enum):
    """Competitive skill-based ranking tiers."""
    UNRANKED = "UNRANKED"
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    DIAMOND = "DIAMOND"
    MASTER = "MASTER"
    ELITE = "ELITE"


class AccountRole(str, Enum):
    """User account privilege roles."""
    PLAYER = "PLAYER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"


class PacketOpcode(int, Enum):
    """Network packet opcodes for fast binary & JSON framing."""
    # Handshake & Session (1-19)
    HANDSHAKE_REQUEST = 1
    HANDSHAKE_RESPONSE = 2
    AUTH_REQUEST = 3
    AUTH_RESPONSE = 4
    DISCONNECT = 5
    HEARTBEAT_PING = 6
    HEARTBEAT_PONG = 7

    # Lobby & Matchmaking (20-39)
    LOBBY_JOIN = 20
    LOBBY_LEAVE = 21
    LOBBY_STATE_UPDATE = 22
    MATCH_SEARCH = 23
    MATCH_FOUND = 24
    MATCH_READY_TOGGLE = 25

    # Gameplay & Simulation (40-69)
    PLAYER_INPUT = 40
    STATE_SNAPSHOT = 41
    DELTA_SNAPSHOT = 42
    COMBAT_ACTION = 43
    HIT_CONFIRMATION = 44
    ABILITY_CAST = 45
    ENTITY_SPAWN = 46
    ENTITY_DESTROY = 47
    PLAYER_DEATH = 48
    PLAYER_RESPAWN = 49

    # World & Objectives (70-89)
    TERRITORY_UPDATE = 70
    WEATHER_CHANGE = 71
    MISSION_ASSIGNED = 72
    MISSION_PROGRESS = 73
    MISSION_COMPLETED = 74
    RESOURCE_HARVESTED = 75
    WORLD_EVENT_TRIGGER = 76

    # Chat & Social (90-99)
    CHAT_MESSAGE = 90
    VOICE_PING = 91
    PING_MARKER = 92

    # Match Lifecycle & End (100-110)
    MATCH_START = 100
    MATCH_END = 101
    MATCH_RESULTS = 102
    ERROR_PACKET = 110


class DisconnectReason(str, Enum):
    """Reasons for connection closure."""
    CLIENT_REQUEST = "CLIENT_REQUEST"
    TIMEOUT = "TIMEOUT"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    SERVER_FULL = "SERVER_FULL"
    MATCH_TERMINATED = "MATCH_TERMINATED"
    KICKED_BY_ADMIN = "KICKED_BY_ADMIN"
    BANNED = "BANNED"
    ANTI_CHEAT_VIOLATION = "ANTI_CHEAT_VIOLATION"
    PROTOCOL_ERROR = "PROTOCOL_ERROR"
    SERVER_RESTART = "SERVER_RESTART"


class ReportCategory(str, Enum):
    """Player moderation report categories."""
    CHEATING = "CHEATING"
    HARASSMENT = "HARASSMENT"
    EXPLOITING = "EXPLOITING"
    AFK_GRIEFING = "AFK_GRIEFING"
    INAPPROPRIATE_NAME = "INAPPROPRIATE_NAME"


class BanDuration(str, Enum):
    """Ban period levels."""
    ONE_HOUR = "1h"
    ONE_DAY = "24h"
    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"
    PERMANENT = "permanent"
