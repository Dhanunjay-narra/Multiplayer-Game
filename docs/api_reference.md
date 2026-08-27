# Nexus Frontier — API Reference

## Authentication (`/api/v1/auth`)

### `POST /api/v1/auth/register`
Creates a new player account, initializing their profile, stats, inventory, and wallet.
- **Request Body**:
  ```json
  {
    "username": "commander_01",
    "email": "commander@nexus.com",
    "password": "SecretPassword123!",
    "role": "PLAYER"
  }
  ```
- **Response `201 Created`**:
  ```json
  {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "token_type": "bearer",
    "expires_in": 14400,
    "user_id": "usr_abc123",
    "username": "commander_01",
    "role": "PLAYER"
  }
  ```

### `POST /api/v1/auth/login`
Authenticates credentials and returns JWT bearer token.

---

## Player & Characters (`/api/v1/player`)

### `GET /api/v1/player/profile`
Fetches complete player profile, level, rank, active faction, and loadout.

### `POST /api/v1/player/character`
Creates a new character class for tactical matches (`VANGUARD`, `INFILTRATOR`, `TECH_ENGINEER`, `NANO_MEDIC`, `STORM_OPERATIVE`).

---

## Lobby & Matchmaking (`/api/v1/lobby`, `/api/v1/matchmaking`)

### `POST /api/v1/lobby/create`
Creates a new match lobby.

### `POST /api/v1/matchmaking/queue`
Enters the skill-based matchmaking queue.

### `GET /api/v1/matchmaking/reservation/{match_id}`
Retrieves dedicated game server connection details for an allocated match.

---

## Economy, Inventory & Crafting (`/api/v1/economy`, `/api/v1/inventory`)

### `GET /api/v1/economy/wallet`
Returns currency balances across Credits, Energy Cells, Alloy Materials, Faction Tokens, and Season Tokens.

### `POST /api/v1/inventory/craft`
Crafts weapons or consumables using raw ingredients.

---

## Live-Ops & Moderation (`/api/v1/admin`, `/api/v1/moderation`)

### `POST /api/v1/admin/config` *(Admin Only)*
Hot-reloads live game balance configs (XP multipliers, harvest rates, weapon damage scales).

### `POST /api/v1/moderation/ban` *(Moderator/Admin Only)*
Applies a ban penalty to a designated player.
