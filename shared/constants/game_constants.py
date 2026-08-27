"""Global physics, networking, and balance constants for Nexus Frontier."""

# Dedicated Server & Networking
SERVER_DEFAULT_TICK_RATE = 30           # 30 updates per second (33.33ms per tick)
SERVER_HIGH_TICK_RATE = 60              # 60 updates per second (16.66ms per tick)
NETWORK_SNAPSHOT_INTERVAL = 3           # Send full or delta snapshot every 3 ticks (10Hz/20Hz)
CLIENT_TIMEOUT_SECONDS = 15.0           # Seconds of silence before client is dropped
RECONNECT_GRACE_PERIOD_SECONDS = 60.0   # Window for reconnecting to an active match
MAX_PACKET_SIZE_BYTES = 65535           # Max UDP/WS payload size
MAX_PLAYERS_PER_MATCH = 16              # Supported session player cap
MIN_PLAYERS_TO_START = 2                # Minimum players to start a session

# World Grid & Boundaries
WORLD_MAP_WIDTH = 2000.0                # World coordinate units (meters)
WORLD_MAP_HEIGHT = 2000.0               # World coordinate units (meters)
TERRITORY_CAPTURE_RADIUS = 35.0         # Units around territory nexus node to capture
TERRITORY_CAPTURE_TIME_SECONDS = 20.0   # Total uncontested capture duration
ENERGY_NODE_EXTRACTION_RATE = 10.0      # Energy units extracted per 10 seconds

# Movement & Physics
BASE_WALK_SPEED = 6.0                   # Meters per second
SPRINT_SPEED_MULTIPLIER = 1.6           # Sprint speed multiplier (9.6 m/s)
CROUCH_SPEED_MULTIPLIER = 0.5           # Crouch speed multiplier (3.0 m/s)
MAX_STAMINA = 100.0
STAMINA_DRAIN_PER_SECOND = 15.0
STAMINA_RECOVERY_PER_SECOND = 25.0
MAX_FALL_DAMAGE = 100.0

# Anti-Cheat Tolerances
MAX_ALLOWED_SPEED_TOLERANCE = 1.25      # 25% margin for lag spikes before flagging speedhack
MAX_TELEPORT_DISTANCE_PER_TICK = 15.0   # Maximum valid displacement in a single tick
MAX_INPUTS_PER_SECOND = 120             # Rate limit for input packets per player
FIRE_RATE_MAX_TOLERANCE = 1.15          # 15% tolerance for weapon fire rate check

# Health, Shields & Combat Defaults
BASE_PLAYER_HEALTH = 100.0
BASE_PLAYER_SHIELD = 100.0
SHIELD_REGEN_DELAY_SECONDS = 5.0        # Delay after taking damage before shield recovers
SHIELD_REGEN_RATE_PER_SECOND = 20.0     # Shield recovery per second
RESPAWN_TIME_SECONDS = 10.0             # Time before dead player respawns at base
KNOCKDOWN_REVIVE_WINDOW_SECONDS = 30.0  # Time team has to revive knocked player
KNOCKDOWN_REVIVE_TIME_SECONDS = 4.0     # Time required to complete a revive

# Economy & Inventory Defaults
DEFAULT_INVENTORY_CAPACITY = 24         # Number of general inventory slots
MAX_ITEM_STACK_SIZE = 999
BASE_STARTING_CREDITS = 1000
MARKETPLACE_TRANSACTION_FEE_PERCENT = 5.0 # 5% tax burned from marketplace trades

# Progression & XP
BASE_XP_PER_KILL = 100
BASE_XP_PER_ASSIST = 40
BASE_XP_PER_TERRITORY_CAPTURE = 250
BASE_XP_PER_MISSION_COMPLETE = 500
BASE_XP_MATCH_WIN = 1000
XP_CURVE_EXPONENT = 1.5                 # Level up cost = 1000 * (level ^ 1.5)
