"""Authoritative 30/60 Hz simulation game loop for dedicated game server instances."""
from __future__ import annotations
import asyncio
import time
import logging
from typing import Dict, List, Optional
from shared.enums.game_enums import GameState, CharacterClass, WeaponType, AbilityType, FactionType, TerritoryState, WeatherType, PacketOpcode
from shared.constants.game_constants import (
    SERVER_DEFAULT_TICK_RATE,
    NETWORK_SNAPSHOT_INTERVAL,
    BASE_WALK_SPEED,
    SPRINT_SPEED_MULTIPLIER,
    CROUCH_SPEED_MULTIPLIER,
    SHIELD_REGEN_DELAY_SECONDS,
    SHIELD_REGEN_RATE_PER_SECOND,
    RESPAWN_TIME_SECONDS,
    TERRITORY_CAPTURE_RADIUS,
    TERRITORY_CAPTURE_TIME_SECONDS,
    BASE_PLAYER_HEALTH,
    BASE_PLAYER_SHIELD,
)
from shared.math.vector import Vector3D
from shared.schemas.gameplay_schemas import (
    PlayerInput,
    PlayerSnapshot,
    PlayerCombatState,
    EntityTransform,
    GameStateSnapshot,
    DeltaSnapshot,
    HitConfirmation,
)
from server.game_server.ecs import (
    EntityManager,
    Entity,
    TransformComponent,
    HealthComponent,
    WeaponComponent,
    AbilityComponent,
    PlayerComponent,
    TerritoryNodeComponent,
    AIControllerComponent,
)
from server.game_server.network_manager import NetworkManager, ClientSession

logger = logging.getLogger("nexus.game_loop")


class DedicatedGameServer:
    """Core authoritative game server simulation engine."""

    def __init__(self, match_id: str, map_id: str = "frontier_nexus_prime", tick_rate: int = SERVER_DEFAULT_TICK_RATE) -> None:
        self.match_id: str = match_id
        self.map_id: str = map_id
        self.tick_rate: int = tick_rate
        self.tick_duration: float = 1.0 / tick_rate
        self.current_tick: int = 0
        self.match_time_remaining: float = 600.0  # 10 minutes
        self.game_state: GameState = GameState.INITIALIZING
        self.winning_team: Optional[str] = None

        self.entity_manager: EntityManager = EntityManager()
        self.network_manager: NetworkManager = NetworkManager()
        self.scores: Dict[str, int] = {"Team_A": 0, "Team_B": 0}
        self.weather_type: WeatherType = WeatherType.CLEAR
        self.weather_duration: float = 300.0

        self._is_running: bool = False
        self._loop_task: Optional[asyncio.Task] = None

    def initialize_world(self) -> None:
        """Spawns static and strategic map elements (Territories, Energy Nodes, AI Defenders)."""
        logger.info(f"Initializing match world: {self.map_id}")

        # Spawn Strategic Territory Nexus A
        node_a = self.entity_manager.create_entity(f"terr_a_{self.match_id}", entity_type="territory")
        node_a.add_component(TransformComponent(position=Vector3D(x=-150.0, y=0.0, z=0.0)))
        node_a.add_component(TerritoryNodeComponent(
            territory_id="terr_alpha",
            name="Alpha Refinery Nexus",
            position=Vector3D(x=-150.0, y=0.0, z=0.0),
            radius=TERRITORY_CAPTURE_RADIUS,
        ))

        # Spawn Strategic Territory Nexus B
        node_b = self.entity_manager.create_entity(f"terr_b_{self.match_id}", entity_type="territory")
        node_b.add_component(TransformComponent(position=Vector3D(x=150.0, y=0.0, z=0.0)))
        node_b.add_component(TerritoryNodeComponent(
            territory_id="terr_bravo",
            name="Bravo Orbital Relay",
            position=Vector3D(x=150.0, y=0.0, z=0.0),
            radius=TERRITORY_CAPTURE_RADIUS,
        ))

        # Spawn NPC Faction Patrol Squad
        for i in range(2):
            npc_id = f"npc_syndicate_{i}_{self.match_id}"
            npc = self.entity_manager.create_entity(npc_id, entity_type="npc")
            npc_pos = Vector3D(x=-50.0 + (i * 100.0), y=0.0, z=100.0)
            npc.add_component(TransformComponent(position=npc_pos))
            npc.add_component(HealthComponent(max_health=120.0, max_shield=60.0))
            npc.add_component(WeaponComponent(primary_weapon=WeaponType.HEAVY_MG))
            npc_ai = AIControllerComponent(faction=FactionType.IRON_SYNDICATE, patrol_radius=60.0)
            npc_ai.patrol_origin = npc_pos
            npc_ai.patrol_target = npc_pos
            npc.add_component(npc_ai)

        self.game_state = GameState.ACTIVE

    def spawn_player(
        self,
        player_id: str,
        username: str,
        team: str = "Team_A",
        character_class: CharacterClass = CharacterClass.VANGUARD,
        spawn_pos: Optional[Vector3D] = None,
    ) -> Entity:
        """Spawns or resets a player character entity in the simulation."""
        if spawn_pos is None:
            spawn_x = -200.0 if team == "Team_A" else 200.0
            spawn_pos = Vector3D(x=spawn_x, y=0.0, z=0.0)

        entity = self.entity_manager.get_entity(player_id)
        if not entity:
            entity = self.entity_manager.create_entity(player_id, entity_type="player")

        entity.add_component(TransformComponent(position=spawn_pos))
        entity.add_component(HealthComponent(max_health=BASE_PLAYER_HEALTH, max_shield=BASE_PLAYER_SHIELD))
        entity.add_component(WeaponComponent())
        entity.add_component(AbilityComponent())
        entity.add_component(PlayerComponent(player_id=player_id, username=username, team=team, character_class=character_class))
        entity.is_active = True
        logger.info(f"Spawned player {username} on {team} at {spawn_pos.to_tuple()}")
        return entity

    async def start(self) -> None:
        """Starts the dedicated server tick loop."""
        self.initialize_world()
        self._is_running = True
        self._loop_task = asyncio.create_task(self._run_loop())
        logger.info(f"Dedicated server started for match {self.match_id} at {self.tick_rate} Hz")

    async def stop(self) -> None:
        """Gracefully halts simulation."""
        self._is_running = False
        self.game_state = GameState.COMPLETED
        if self._loop_task:
            self._loop_task.cancel()
        logger.info(f"Dedicated server stopped for match {self.match_id}")

    async def _run_loop(self) -> None:
        """Main fixed-timestep simulation tick loop."""
        while self._is_running:
            tick_start = time.time()
            try:
                await self.tick(self.tick_duration)
            except Exception as e:
                logger.error(f"Error in simulation tick {self.current_tick}: {e}", exc_info=True)

            elapsed = time.time() - tick_start
            sleep_time = max(0.0, self.tick_duration - elapsed)
            await asyncio.sleep(sleep_time)

    async def tick(self, delta_time: float) -> None:
        """Executes a single simulation tick."""
        self.current_tick += 1
        self.match_time_remaining = max(0.0, self.match_time_remaining - delta_time)

        # 1. Process client input packets
        await self._process_network_inputs(delta_time)

        # 2. Update health & shield regeneration
        self._update_combat_recovery(delta_time)

        # 3. Update NPC AI state machines
        self._update_ai_controllers(delta_time)

        # 4. Update territory capture points
        self._update_territory_nodes(delta_time)

        # 5. Check match victory conditions
        self._check_match_rules()

        # 6. Broadcast state snapshot every N ticks
        if self.current_tick % NETWORK_SNAPSHOT_INTERVAL == 0:
            await self._broadcast_snapshot()

    async def _process_network_inputs(self, delta_time: float) -> None:
        """Reads input packets and performs authoritative physics and action updates."""
        packets = await self.network_manager.poll_inbound_packets()
        for packet in packets:
            sender_id = packet.header.sender_id
            if not sender_id:
                continue

            entity = self.entity_manager.get_entity(sender_id)
            if not entity or not entity.is_active:
                continue

            transform = entity.get_component(TransformComponent)
            health = entity.get_component(HealthComponent)
            player_comp = entity.get_component(PlayerComponent)
            session = self.network_manager.get_session(sender_id)

            if not transform or not health or not health.is_alive:
                continue

            if packet.header.opcode == PacketOpcode.PLAYER_INPUT:
                data = packet.payload
                input_seq = data.get("input_seq", 0)
                if player_comp:
                    player_comp.last_input_sequence = input_seq

                # Movement integration
                mv_x = float(data.get("move_x", 0.0))
                mv_z = float(data.get("move_z", 0.0))
                is_sprint = bool(data.get("sprint", False))
                is_crouch = bool(data.get("crouch", False))

                speed = BASE_WALK_SPEED
                if is_sprint:
                    speed *= SPRINT_SPEED_MULTIPLIER
                elif is_crouch:
                    speed *= CROUCH_SPEED_MULTIPLIER

                desired_velocity = Vector3D(x=mv_x * speed, y=0.0, z=mv_z * speed)
                target_position = transform.position + (desired_velocity * delta_time)

                # Authoritative anti-cheat validation
                if session and not self.network_manager.validate_movement_delta(session, transform.position, target_position, delta_time, is_sprint):
                    # Reject movement if invalid
                    pass
                else:
                    transform.velocity = desired_velocity
                    transform.position = target_position

                transform.yaw = float(data.get("yaw", transform.yaw))
                transform.pitch = float(data.get("pitch", transform.pitch))

            elif packet.header.opcode == PacketOpcode.COMBAT_ACTION:
                self._handle_combat_action(sender_id, packet.payload)

    def _handle_combat_action(self, shooter_id: str, data: Dict[str, Any]) -> None:
        """Processes weapon firing or melee combat."""
        shooter = self.entity_manager.get_entity(shooter_id)
        if not shooter or not shooter.is_active:
            return

        weapon = shooter.get_component(WeaponComponent)
        if not weapon or weapon.ammo_in_clip <= 0 or weapon.fire_cooldown_remaining > 0:
            return

        weapon.ammo_in_clip -= 1
        weapon.fire_cooldown_remaining = 0.1  # Fire rate throttle
        target_id = data.get("target_id")
        if target_id:
            self.apply_damage(shooter_id, target_id, damage_amount=34.0, hit_location=data.get("hit_loc", "body"))

    def apply_damage(self, attacker_id: str, target_id: str, damage_amount: float, hit_location: str = "body") -> Optional[HitConfirmation]:
        """Calculates authoritative damage with shield absorption and death detection."""
        target = self.entity_manager.get_entity(target_id)
        if not target or not target.is_active:
            return None

        health = target.get_component(HealthComponent)
        if not health or not health.is_alive:
            return None

        # Critical damage multiplier for headshots
        is_crit = hit_location.lower() == "head"
        if is_crit:
            damage_amount *= 1.75

        # Shield absorbs damage first
        absorbed_by_shield = min(health.shield, damage_amount)
        health.shield -= absorbed_by_shield
        remaining_dmg = damage_amount - absorbed_by_shield
        health.health = max(0.0, health.health - remaining_dmg)
        health.last_damage_time = time.time()

        # Track attacker stats
        attacker = self.entity_manager.get_entity(attacker_id)
        if attacker:
            att_player = attacker.get_component(PlayerComponent)
            if att_player:
                att_player.damage_dealt += damage_amount

        target_killed = False
        if health.health <= 0.0:
            health.is_alive = False
            health.respawn_timer = RESPAWN_TIME_SECONDS
            target_killed = True

            # Score update & kill attribution
            if attacker:
                att_player = attacker.get_component(PlayerComponent)
                if att_player:
                    att_player.kills += 1
                    self.scores[att_player.team] = self.scores.get(att_player.team, 0) + 1

            tar_player = target.get_component(PlayerComponent)
            if tar_player:
                tar_player.deaths += 1

            logger.info(f"Player {target_id} eliminated by {attacker_id} ({hit_location})")

        return HitConfirmation(
            shooter_id=attacker_id,
            target_id=target_id,
            hit_location=hit_location,
            damage_dealt=damage_amount,
            shield_absorbed=absorbed_by_shield,
            target_remaining_health=health.health,
            target_killed=target_killed,
            critical_hit=is_crit,
        )

    def _update_combat_recovery(self, delta_time: float) -> None:
        """Handles shield regeneration after cooldown and respawns dead entities."""
        now = time.time()
        for entity in self.entity_manager.get_entities_with(HealthComponent):
            health = entity.get_component(HealthComponent)
            if not health:
                continue

            if not health.is_alive:
                health.respawn_timer -= delta_time
                if health.respawn_timer <= 0:
                    health.is_alive = True
                    health.health = health.max_health
                    health.shield = health.max_shield
                    transform = entity.get_component(TransformComponent)
                    if transform:
                        transform.position = Vector3D(x=0.0, y=0.0, z=0.0)
                    logger.info(f"Entity {entity.id} respawned")
            else:
                # Shield regeneration (if not in ion storm)
                if self.weather_type != WeatherType.ION_STORM:
                    if now - health.last_damage_time >= SHIELD_REGEN_DELAY_SECONDS:
                        if health.shield < health.max_shield:
                            health.shield = min(health.max_shield, health.shield + (SHIELD_REGEN_RATE_PER_SECOND * delta_time))

    def _update_ai_controllers(self, delta_time: float) -> None:
        """Executes basic perception and patrol navigation for AI controllers."""
        for entity in self.entity_manager.get_entities_with(AIControllerComponent, TransformComponent):
            ai = entity.get_component(AIControllerComponent)
            transform = entity.get_component(TransformComponent)
            if not ai or not transform:
                continue

            # Patrol movement around anchor point
            dist = transform.position.distance_to(ai.patrol_target)
            if dist < 2.0:
                # Pick new target in patrol radius
                ai.patrol_target = ai.patrol_origin + Vector3D(x=20.0, y=0.0, z=20.0)
            else:
                dir_vec = (ai.patrol_target - transform.position).normalized()
                transform.position = transform.position + (dir_vec * (BASE_WALK_SPEED * 0.7 * delta_time))

    def _update_territory_nodes(self, delta_time: float) -> None:
        """Updates territory capture status when players enter capture perimeter."""
        for entity in self.entity_manager.get_entities_with(TerritoryNodeComponent, TransformComponent):
            terr = entity.get_component(TerritoryNodeComponent)
            transform = entity.get_component(TransformComponent)
            if not terr or not transform:
                continue

            # Check players inside radius
            team_a_count = 0
            team_b_count = 0

            for player_ent in self.entity_manager.get_entities_with(PlayerComponent, TransformComponent, HealthComponent):
                p_trans = player_ent.get_component(TransformComponent)
                p_health = player_ent.get_component(HealthComponent)
                p_comp = player_ent.get_component(PlayerComponent)
                if not p_trans or not p_health or not p_comp or not p_health.is_alive:
                    continue

                if p_trans.position.distance_to(transform.position) <= terr.radius:
                    if p_comp.team == "Team_A":
                        team_a_count += 1
                    elif p_comp.team == "Team_B":
                        team_b_count += 1

            if team_a_count > 0 and team_b_count == 0:
                terr.capture_progress = min(100.0, terr.capture_progress + ((100.0 / TERRITORY_CAPTURE_TIME_SECONDS) * delta_time))
                if terr.capture_progress >= 100.0:
                    terr.owner_faction = FactionType.SOLARIS_HEGEMONY
                    terr.state = TerritoryState.FORTIFIED
            elif team_b_count > 0 and team_a_count == 0:
                terr.capture_progress = max(0.0, terr.capture_progress - ((100.0 / TERRITORY_CAPTURE_TIME_SECONDS) * delta_time))
                if terr.capture_progress <= 0.0:
                    terr.owner_faction = FactionType.IRON_SYNDICATE
                    terr.state = TerritoryState.FORTIFIED

    def _check_match_rules(self) -> None:
        """Checks for match completion (score limit or time expiry)."""
        if self.game_state != GameState.ACTIVE:
            return

        if self.match_time_remaining <= 0 or self.scores["Team_A"] >= 30 or self.scores["Team_B"] >= 30:
            self.game_state = GameState.COMPLETED
            if self.scores["Team_A"] > self.scores["Team_B"]:
                self.winning_team = "Team_A"
            elif self.scores["Team_B"] > self.scores["Team_A"]:
                self.winning_team = "Team_B"
            else:
                self.winning_team = "DRAW"
            logger.info(f"Match {self.match_id} completed! Winner: {self.winning_team}")

    def create_snapshot(self) -> GameStateSnapshot:
        """Constructs an authoritative GameStateSnapshot of the current world."""
        players_snapshot: Dict[str, PlayerSnapshot] = {}

        for entity in self.entity_manager.get_entities_with(PlayerComponent, TransformComponent, HealthComponent, WeaponComponent):
            player_comp = entity.get_component(PlayerComponent)
            transform = entity.get_component(TransformComponent)
            health = entity.get_component(HealthComponent)
            weapon = entity.get_component(WeaponComponent)
            if not player_comp or not transform or not health or not weapon:
                continue

            players_snapshot[entity.id] = PlayerSnapshot(
                player_id=player_comp.player_id,
                username=player_comp.username,
                team=player_comp.team,
                character_class=player_comp.character_class,
                transform=EntityTransform(
                    position=transform.position,
                    velocity=transform.velocity,
                    rotation_yaw=transform.yaw,
                    rotation_pitch=transform.pitch,
                ),
                combat_state=PlayerCombatState(
                    health=health.health,
                    max_health=health.max_health,
                    shield=health.shield,
                    max_shield=health.max_shield,
                    is_alive=health.is_alive,
                    is_knocked=health.is_knocked,
                    active_weapon=weapon.primary_weapon,
                    ammo_in_clip=weapon.ammo_in_clip,
                    reserve_ammo=weapon.reserve_ammo,
                ),
                ping_ms=player_comp.ping_ms,
            )

        return GameStateSnapshot(
            server_tick=self.current_tick,
            server_time=time.time(),
            players=players_snapshot,
            projectiles=[],
            scores=self.scores,
            match_time_remaining=self.match_time_remaining,
        )

    async def _broadcast_snapshot(self) -> None:
        """Broadcasts current snapshot to all active client sessions."""
        snapshot = self.create_snapshot()
        await self.network_manager.broadcast_packet(
            opcode=PacketOpcode.STATE_SNAPSHOT,
            payload=snapshot.model_dump(),
        )
