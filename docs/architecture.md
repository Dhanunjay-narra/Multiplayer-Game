# Nexus Frontier — Technical Architecture Specification

## 1. System Overview

**Nexus Frontier** is a dedicated-server multiplayer tactical action, strategy, and exploration platform.
Every multiplayer match runs on an authoritative dedicated game server and directly influences the persistent game world.

---

## 2. Component Topology

```
+-----------------------------------------------------------------------------------+
|                                  GAME CLIENT                                      |
|  +-----------------+  +------------------+  +-----------------+  +-------------+  |
|  |  Game Engine    |  | Client Prediction|  |  Reconciliation |  | Terminal UI |  |
|  +-----------------+  +------------------+  +-----------------+  +-------------+  |
+-----------------------------------------------------------------------------------+
                                         |
                       Binary & JSON UDP/WebSocket Protocol
                                         |
+-----------------------------------------------------------------------------------+
|                            DEDICATED GAME SERVER                                  |
|  +-----------------------------------------------------------------------------+  |
|  | Authoritative Tick Loop (30/60 Hz)                                          |  |
|  |  * Entity Component System (ECS)                                            |  |
|  |  * Physics & Movement Anti-Cheat Validation                                 |  |
|  |  * Ballistics, Hitscan & Damage Mitigation (Health / Shield / Armor)         |  |
|  |  * Tactical Abilities (Shield Dome, EMP, Recon Radar, Nanite Heal)          |  |
|  |  * Multi-Agent NPC AI (Perception Vision Cones, Sound, Behavior Trees)      |  |
|  |  * Dynamic Strategic Territories & Energy Extraction Nodes                  |  |
|  |  * State Snapshot & Delta Compression Broadcast Engine                     |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
                                         |
                       Domain Events & Match Results
                                         |
+-----------------------------------------------------------------------------------+
|                           API GATEWAY PLATFORM SERVICES                           |
|  +---------------+  +----------------+  +------------------+  +----------------+  |
|  | Auth & RBAC   |  | Player Profiles|  | Matchmaker & MMR |  | Lobbies/Parties|  |
|  +---------------+  +----------------+  +------------------+  +----------------+  |
|  +---------------+  +----------------+  +------------------+  +----------------+  |
|  | Inventory &   |  | Multi-Currency |  | Dynamic Mission  |  | Factions &     |  |
|  | Crafting      |  | Wallet Ledger  |  | & Event Engine   |  | Territories    |  |
|  +---------------+  +----------------+  +------------------+  +----------------+  |
|  +---------------+  +----------------+  +------------------+  +----------------+  |
|  | Social & Clan |  | Live-Ops Config|  | Moderation &     |  | Telemetry &    |  |
|  | Channels      |  | & Audit Logs   |  | Anti-Cheat Bans  |  | Replay Stream  |  |
|  +---------------+  +----------------+  +------------------+  +----------------+  |
+-----------------------------------------------------------------------------------+
                                         |
                               Async Database Layer
                                         |
+-----------------------------------------------------------------------------------+
|                        PostgreSQL / Redis / Object Storage                        |
+-----------------------------------------------------------------------------------+
```

---

## 3. Network Protocol & Tick Lifecycle

1. **Input Dispatch**: Client sends input packets (`move_x`, `move_z`, `yaw`, `pitch`, `is_sprinting`, `actions`).
2. **Server Authoritative Step**:
   - Checks input rate limit (< 120 packets/sec).
   - Validates maximum displacement per tick against speed limit.
   - Updates positions and orientations.
   - Advances weapon cooldowns and reload timers.
   - Advances dynamic weather and territory capture radius timers.
   - Evaluates AI sensors (vision cones, threat score) and behavior tree actions.
3. **State Snapshot Broadcast**:
   - Full or delta compressed snapshots broadcast every `N` ticks (e.g. every 3 ticks at 30 Hz = 10 updates/sec).
   - Clients reconcile local predicted transforms against authoritative snapshots.

---

## 4. Persistent World & Factions

The persistent galaxy is contested by five core factions:
- **Solaris Hegemony**: High-tech energy shields, precision lasers.
- **Iron Syndicate**: Ballistic kinetics, heavy armor, industrial mining.
- **Cyber Nexus**: Electronic warfare, EMP disruption, autonomous drones.
- **Void Outcasts**: Bio-enhancement stims, guerrilla stealth tactics.
- **Neutral / Mercenary**: Unaligned resource trading outposts.
