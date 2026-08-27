"""Player profile, character management, and stats service."""
import uuid
import time
import math
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.db_models import User, PlayerProfileModel, Character, LoadoutModel, PlayerStatsModel
from shared.schemas.player_schemas import CharacterCreateRequest, LoadoutConfig, PlayerProfile, PlayerStats
from shared.enums.game_enums import CharacterClass, FactionType, RankTier, WeaponType, AbilityType
from shared.constants.game_constants import XP_CURVE_EXPONENT


class PlayerService:
    """Manages player profiles, characters, stats, and loadouts."""

    def calculate_required_xp(self, level: int) -> int:
        """Computes XP needed for next level using exponential curve."""
        return int(1000 * math.pow(level, XP_CURVE_EXPONENT))

    async def get_player_profile(self, session: AsyncSession, user_id: str) -> PlayerProfile:
        """Loads complete player profile with stats and active loadout."""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        stmt_prof = select(PlayerProfileModel).where(PlayerProfileModel.user_id == user_id)
        res_prof = await session.execute(stmt_prof)
        profile_model = res_prof.scalar_one_or_none()
        if not profile_model:
            raise ValueError("Player profile not found")

        stmt_stats = select(PlayerStatsModel).where(PlayerStatsModel.profile_id == profile_model.id)
        res_stats = await session.execute(stmt_stats)
        stats_model = res_stats.scalar_one_or_none()

        stats = PlayerStats()
        if stats_model:
            stats = PlayerStats(
                matches_played=stats_model.matches_played,
                matches_won=stats_model.matches_won,
                kills=stats_model.kills,
                deaths=stats_model.deaths,
                assists=stats_model.assists,
                territories_captured=stats_model.territories_captured,
                missions_completed=stats_model.missions_completed,
                resources_extracted=stats_model.resources_extracted,
                total_damage_dealt=stats_model.total_damage_dealt,
            )

        # Active loadout
        stmt_char = select(Character).where(Character.user_id == user_id)
        res_char = await session.execute(stmt_char)
        char = res_char.scalars().first()

        active_loadout = LoadoutConfig(loadout_id="default_loadout")
        if char:
            stmt_loadout = select(LoadoutModel).where(LoadoutModel.character_id == char.id, LoadoutModel.is_active == True)
            res_loadout = await session.execute(stmt_loadout)
            loadout_model = res_loadout.scalar_one_or_none()
            if loadout_model:
                active_loadout = LoadoutConfig(
                    loadout_id=loadout_model.id,
                    name=loadout_model.name,
                    primary_weapon=WeaponType(loadout_model.primary_weapon),
                    secondary_weapon=WeaponType(loadout_model.secondary_weapon),
                    primary_ability=AbilityType(loadout_model.primary_ability),
                    secondary_ability=AbilityType(loadout_model.secondary_ability),
                )

        return PlayerProfile(
            player_id=user.id,
            username=user.username,
            avatar_url=profile_model.avatar_url,
            level=profile_model.level,
            current_xp=profile_model.current_xp,
            next_level_xp=self.calculate_required_xp(profile_model.level),
            rank_tier=RankTier(profile_model.rank_tier),
            rank_points=profile_model.rank_points,
            active_faction=FactionType(profile_model.active_faction),
            stats=stats,
            active_loadout=active_loadout,
        )

    async def create_character(self, session: AsyncSession, user_id: str, req: CharacterCreateRequest) -> Character:
        """Creates a new playable character with default class loadout."""
        char_id = f"char_{uuid.uuid4().hex[:12]}"
        char_class_str = req.character_class.value if hasattr(req.character_class, "value") else str(req.character_class)
        faction_str = req.faction.value if hasattr(req.faction, "value") else str(req.faction)
        char = Character(
            id=char_id,
            user_id=user_id,
            name=req.character_name,
            character_class=char_class_str,
            faction=faction_str,
            created_at=time.time(),
        )
        session.add(char)

        # Default class abilities & weapons
        default_weapon = WeaponType.ASSAULT_RIFLE
        default_ability = AbilityType.SHIELD_DOME

        if req.character_class == CharacterClass.INFILTRATOR:
            default_weapon = WeaponType.PLASMA_SNIPER
            default_ability = AbilityType.CLOAKING
        elif req.character_class == CharacterClass.TECH_ENGINEER:
            default_weapon = WeaponType.ARC_CANNON
            default_ability = AbilityType.ATTACK_DRONE
        elif req.character_class == CharacterClass.NANO_MEDIC:
            default_weapon = WeaponType.ASSAULT_RIFLE
            default_ability = AbilityType.NANO_HEAL_FIELD
        elif req.character_class == CharacterClass.STORM_OPERATIVE:
            default_weapon = WeaponType.HEAVY_MG
            default_ability = AbilityType.EMP_BURST

        loadout = LoadoutModel(
            id=f"ldo_{uuid.uuid4().hex[:12]}",
            character_id=char_id,
            name="Default Class Loadout",
            primary_weapon=default_weapon.value if hasattr(default_weapon, "value") else str(default_weapon),
            secondary_weapon=WeaponType.TACTICAL_PISTOL.value,
            primary_ability=default_ability.value if hasattr(default_ability, "value") else str(default_ability),
            secondary_ability=AbilityType.RECON_RADAR.value,
            is_active=True,
        )
        session.add(loadout)
        await session.commit()
        return char

    async def add_xp(self, session: AsyncSession, user_id: str, xp_amount: int) -> bool:
        """Awards XP to player profile and levels up if threshold reached."""
        stmt = select(PlayerProfileModel).where(PlayerProfileModel.user_id == user_id)
        result = await session.execute(stmt)
        profile = result.scalar_one_or_none()
        if not profile:
            return False

        profile.current_xp += xp_amount
        leveled_up = False
        while True:
            req_xp = self.calculate_required_xp(profile.level)
            if profile.current_xp >= req_xp:
                profile.current_xp -= req_xp
                profile.level += 1
                leveled_up = True
            else:
                break

        await session.commit()
        return leveled_up


player_service = PlayerService()
