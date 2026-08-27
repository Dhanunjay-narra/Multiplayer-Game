"""Interactive terminal client dashboard with live radar, HUD, and combat log."""
import time
from typing import Dict, List, Optional
from shared.schemas.gameplay_schemas import GameStateSnapshot

try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class TerminalClientUI:
    """Interactive terminal interface for Nexus Frontier players."""

    def __init__(self, player_id: str, username: str) -> None:
        self.player_id = player_id
        self.username = username
        if RICH_AVAILABLE:
            self.console = Console()

    def render_hud(self, snapshot: GameStateSnapshot) -> None:
        """Renders live tactical game HUD."""
        my_snap = snapshot.players.get(self.player_id)
        if not my_snap:
            print(f"Waiting for spawn... Match Time: {snapshot.match_time_remaining:.1f}s")
            return

        hp = my_snap.combat_state.health
        shield = my_snap.combat_state.shield
        weapon = my_snap.combat_state.active_weapon
        ammo = f"{my_snap.combat_state.ammo_in_clip}/{my_snap.combat_state.reserve_ammo}"
        scores = f"Team A: {snapshot.scores.get('Team_A', 0)} | Team B: {snapshot.scores.get('Team_B', 0)}"

        if RICH_AVAILABLE:
            table = Table(title="NEXUS FRONTIER - TACTICAL HUD", style="cyan")
            table.add_column("Stat", style="bold white")
            table.add_column("Value", style="green")
            table.add_row("Health", f"[{'#' * int(hp / 10)}{'.' * (10 - int(hp / 10))}] {hp:.0f}/100")
            table.add_row("Shield", f"[{'#' * int(shield / 10)}{'.' * (10 - int(shield / 10))}] {shield:.0f}/100")
            table.add_row("Weapon", f"{weapon} ({ammo})")
            table.add_row("Team Score", scores)
            table.add_row("Time Left", f"{snapshot.match_time_remaining:.1f}s")
            self.console.print(table)
        else:
            hp_bar = '#' * int(hp / 10) + '.' * (10 - int(hp / 10))
            shield_bar = '#' * int(shield / 10) + '.' * (10 - int(shield / 10))
            print("-" * 55)
            print(f">> NEXUS FRONTIER HUD | {self.username} [{scores}]")
            print(f"  HP:     [{hp_bar}] {hp:.0f}/100")
            print(f"  SHIELD: [{shield_bar}] {shield:.0f}/100")
            print(f"  WEAPON: {weapon} ({ammo}) | TIME: {snapshot.match_time_remaining:.1f}s")
            print("-" * 55)
