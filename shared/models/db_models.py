"""SQLAlchemy ORM models defining the relational database schema."""
import time
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    Text,
    DateTime,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True)
    username = Column(String(32), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), default="PLAYER")
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    created_at = Column(Float, default=lambda: time.time())
    updated_at = Column(Float, default=lambda: time.time())

    characters = relationship("Character", back_populates="user", cascade="all, delete-orphan")
    player_profile = relationship("PlayerProfileModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    wallet = relationship("WalletModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    inventory = relationship("InventoryModel", back_populates="user", uselist=False, cascade="all, delete-orphan")


class PlayerProfileModel(Base):
    __tablename__ = "player_profiles"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    level = Column(Integer, default=1)
    current_xp = Column(Integer, default=0)
    rank_tier = Column(String(20), default="UNRANKED")
    rank_points = Column(Integer, default=0)
    mmr = Column(Integer, default=1200)
    active_faction = Column(String(32), default="SOLARIS_HEGEMONY")
    avatar_url = Column(String(256), nullable=True)

    user = relationship("User", back_populates="player_profile")
    stats = relationship("PlayerStatsModel", back_populates="profile", uselist=False, cascade="all, delete-orphan")


class Character(Base):
    __tablename__ = "characters"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(32), nullable=False)
    character_class = Column(String(32), nullable=False)
    faction = Column(String(32), nullable=False)
    created_at = Column(Float, default=lambda: time.time())

    user = relationship("User", back_populates="characters")
    loadouts = relationship("LoadoutModel", back_populates="character", cascade="all, delete-orphan")


class LoadoutModel(Base):
    __tablename__ = "loadouts"
    id = Column(String(36), primary_key=True)
    character_id = Column(String(36), ForeignKey("characters.id"), nullable=False)
    name = Column(String(64), default="Default Loadout")
    primary_weapon = Column(String(32), default="ASSAULT_RIFLE")
    secondary_weapon = Column(String(32), default="TACTICAL_PISTOL")
    primary_ability = Column(String(32), default="SHIELD_DOME")
    secondary_ability = Column(String(32), default="RECON_RADAR")
    is_active = Column(Boolean, default=True)

    character = relationship("Character", back_populates="loadouts")


class PlayerStatsModel(Base):
    __tablename__ = "player_stats"
    id = Column(String(36), primary_key=True)
    profile_id = Column(String(36), ForeignKey("player_profiles.id"), unique=True, nullable=False)
    matches_played = Column(Integer, default=0)
    matches_won = Column(Integer, default=0)
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    territories_captured = Column(Integer, default=0)
    missions_completed = Column(Integer, default=0)
    resources_extracted = Column(Float, default=0.0)
    total_damage_dealt = Column(Float, default=0.0)

    profile = relationship("PlayerProfileModel", back_populates="stats")


class InventoryModel(Base):
    __tablename__ = "inventories"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    max_slots = Column(Integer, default=24)

    user = relationship("User", back_populates="inventory")
    items = relationship("InventoryItemModel", back_populates="inventory", cascade="all, delete-orphan")


class InventoryItemModel(Base):
    __tablename__ = "inventory_items"
    id = Column(String(36), primary_key=True)
    inventory_id = Column(String(36), ForeignKey("inventories.id"), nullable=False)
    slot_index = Column(Integer, nullable=False)
    template_id = Column(String(64), nullable=False)
    name = Column(String(64), nullable=False)
    category = Column(String(32), nullable=False)
    rarity = Column(String(20), default="COMMON")
    quantity = Column(Integer, default=1)
    durability = Column(Float, default=100.0)
    is_locked = Column(Boolean, default=False)
    attributes = Column(JSON, default=dict)

    inventory = relationship("InventoryModel", back_populates="items")


class WalletModel(Base):
    __tablename__ = "wallets"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    credits = Column(Float, default=1000.0)
    energy_cells = Column(Float, default=100.0)
    alloy_materials = Column(Float, default=50.0)
    faction_tokens = Column(Float, default=0.0)
    season_tokens = Column(Float, default=0.0)

    user = relationship("User", back_populates="wallet")


class TransactionModel(Base):
    __tablename__ = "transactions"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    currency = Column(String(32), nullable=False)
    amount = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    description = Column(String(256), nullable=False)
    timestamp = Column(Float, default=lambda: time.time())


class MatchModel(Base):
    __tablename__ = "matches"
    id = Column(String(36), primary_key=True)
    map_id = Column(String(64), nullable=False)
    server_address = Column(String(128), nullable=False)
    server_port = Column(Integer, nullable=False)
    game_state = Column(String(32), default="ACTIVE")
    winning_team = Column(String(32), nullable=True)
    started_at = Column(Float, default=lambda: time.time())
    ended_at = Column(Float, nullable=True)
    match_duration = Column(Float, nullable=True)


class MatchPlayerModel(Base):
    __tablename__ = "match_players"
    id = Column(String(36), primary_key=True)
    match_id = Column(String(36), ForeignKey("matches.id"), index=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    team = Column(String(32), nullable=False)
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    damage_dealt = Column(Float, default=0.0)
    xp_earned = Column(Integer, default=0)
    credits_earned = Column(Float, default=0.0)


class ClanModel(Base):
    __tablename__ = "clans"
    id = Column(String(36), primary_key=True)
    name = Column(String(32), unique=True, index=True, nullable=False)
    tag = Column(String(6), unique=True, index=True, nullable=False)
    faction_alignment = Column(String(32), default="SOLARIS_HEGEMONY")
    level = Column(Integer, default=1)
    total_reputation = Column(Integer, default=0)
    motd = Column(String(256), default="Welcome to Nexus Frontier")
    created_at = Column(Float, default=lambda: time.time())

    members = relationship("ClanMemberModel", back_populates="clan", cascade="all, delete-orphan")


class ClanMemberModel(Base):
    __tablename__ = "clan_members"
    id = Column(String(36), primary_key=True)
    clan_id = Column(String(36), ForeignKey("clans.id"), index=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    role = Column(String(20), default="MEMBER")
    contributed_xp = Column(Integer, default=0)
    joined_at = Column(Float, default=lambda: time.time())

    clan = relationship("ClanModel", back_populates="members")


class TerritoryModel(Base):
    __tablename__ = "territories"
    id = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False)
    controlling_faction = Column(String(32), default="NEUTRAL")
    state = Column(String(32), default="UNCONTESTED")
    defense_level = Column(Integer, default=1)
    strategic_value = Column(Integer, default=100)
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=0.0)
    pos_z = Column(Float, default=0.0)
    updated_at = Column(Float, default=lambda: time.time())


class ReportModel(Base):
    __tablename__ = "reports"
    id = Column(String(36), primary_key=True)
    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    reported_user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    category = Column(String(32), nullable=False)
    details = Column(Text, nullable=False)
    match_id = Column(String(36), nullable=True)
    status = Column(String(20), default="PENDING")
    created_at = Column(Float, default=lambda: time.time())


class BanModel(Base):
    __tablename__ = "bans"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    issued_by = Column(String(36), nullable=False)
    reason = Column(String(256), nullable=False)
    duration = Column(String(20), nullable=False)
    category = Column(String(32), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(Float, default=lambda: time.time())
    expires_at = Column(Float, nullable=True)


class AuditLogModel(Base):
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True)
    actor_id = Column(String(36), nullable=False)
    action_type = Column(String(64), nullable=False)
    target_id = Column(String(36), nullable=True)
    details = Column(JSON, default=dict)
    timestamp = Column(Float, default=lambda: time.time())
