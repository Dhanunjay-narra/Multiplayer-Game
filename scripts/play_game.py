"""Interactive Turn/Real-time CLI Playable Game for Nexus Frontier."""
import os
import sys
import time
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.game_server.game_loop import DedicatedGameServer
from server.combat.weapons import WEAPON_DEFINITIONS, WeaponType
from server.combat.abilities import ABILITY_DEFINITIONS, AbilityType
from shared.enums.game_enums import CharacterClass, FactionType
from shared.math.vector import Vector3D


def main():
    print("=" * 65)
    print("      NEXUS FRONTIER: INTERACTIVE TACTICAL COMBAT ARENA")
    print("=" * 65)

    print("\nSelect your Tactical Class:")
    print("  [1] VANGUARD       - Heavy Shields, High HP, Assault Rifle, Shield Dome")
    print("  [2] INFILTRATOR    - Stealth Cloaking, Plasma Sniper, High Crit")
    print("  [3] TECH ENGINEER  - Autonomous Drone, Arc Cannon, EMP Surge")
    print("  [4] NANO MEDIC     - Nano-Healing Field, Stim Booster, Sustain")

    choice = input("\nEnter choice (1-4, default 1): ").strip()
    class_map = {
        "1": (CharacterClass.VANGUARD, WeaponType.ASSAULT_RIFLE, AbilityType.SHIELD_DOME),
        "2": (CharacterClass.INFILTRATOR, WeaponType.PLASMA_SNIPER, AbilityType.CLOAKING),
        "3": (CharacterClass.TECH_ENGINEER, WeaponType.ARC_CANNON, AbilityType.EMP_BURST),
        "4": (CharacterClass.NANO_MEDIC, WeaponType.ASSAULT_RIFLE, AbilityType.NANO_HEAL_FIELD),
    }
    selected_class, selected_weapon, selected_ability = class_map.get(choice, class_map["1"])

    player_name = input("Enter your Call-Sign [Commander]: ").strip() or "Commander"
    print(f"\nWelcome, {player_name}! Deploying as {selected_class.value} with {selected_weapon.value}...\n")

    # Game State
    player_pos = Vector3D(x=0.0, y=0.0, z=0.0)
    player_hp = 100.0
    player_shield = 100.0
    ammo = 30
    reserve_ammo = 180
    kills = 0
    score_a = 0
    score_b = 0
    ability_cd = 0

    # Enemy Squad
    enemies = [
        {"name": "Syndicate Enforcer", "pos": Vector3D(x=25.0, y=0.0, z=15.0), "hp": 80.0, "shield": 50.0},
        {"name": "Syndicate Sniper", "pos": Vector3D(x=-30.0, y=0.0, z=40.0), "hp": 60.0, "shield": 40.0},
        {"name": "Syndicate Vanguard", "pos": Vector3D(x=10.0, y=0.0, z=60.0), "hp": 120.0, "shield": 80.0},
    ]

    territory_progress = 0.0

    print("-" * 65)
    print("MISSION: Eliminate hostile Iron Syndicate squad & capture Central Spire!")
    print("-" * 65)

    while player_hp > 0 and len([e for e in enemies if e["hp"] > 0]) > 0:
        active_enemies = [e for e in enemies if e["hp"] > 0]
        
        # Display HUD
        hp_bar = '#' * int(player_hp / 10) + '.' * (10 - int(player_hp / 10))
        shield_bar = '#' * int(player_shield / 10) + '.' * (10 - int(player_shield / 10))
        print(f"\n>> {player_name} [{selected_class.value}] | Pos: ({player_pos.x:.0f}, {player_pos.z:.0f})")
        print(f"   HP:     [{hp_bar}] {player_hp:.0f}/100")
        print(f"   SHIELD: [{shield_bar}] {player_shield:.0f}/100")
        print(f"   WEAPON: {selected_weapon.value} ({ammo}/{reserve_ammo}) | ABILITY: {selected_ability.value} {'[READY]' if ability_cd == 0 else f'[CD: {ability_cd}]'}")
        print(f"   CENTRAL SPIRE CAPTURE: {territory_progress:.0f}% | ENEMIES REMAINING: {len(active_enemies)}")

        print("\nCommands: [w/a/s/d] Move | [f] Fire Weapon | [e] Use Ability | [r] Reload | [c] Capture Node | [q] Quit")
        cmd = input("Tactical Action > ").strip().lower()

        if cmd == "q":
            print("Mission aborted.")
            break
        elif cmd in ["w", "a", "s", "d"]:
            if cmd == "w": player_pos.z += 15.0
            elif cmd == "s": player_pos.z -= 15.0
            elif cmd == "a": player_pos.x -= 15.0
            elif cmd == "d": player_pos.x += 15.0
            print(f">> Moved to ({player_pos.x:.0f}, {player_pos.z:.0f})")
        elif cmd == "r":
            ammo = 30
            print(">> Reloaded weapon clip.")
        elif cmd == "e":
            if ability_cd == 0:
                ability_cd = 3
                if selected_ability == AbilityType.SHIELD_DOME:
                    player_shield = min(100.0, player_shield + 50.0)
                    print(">> Aegis Shield Dome deployed! (+50 Shield)")
                elif selected_ability == AbilityType.EMP_BURST:
                    for e in active_enemies:
                        e["shield"] = 0.0
                    print(">> EMP Shockwave blasted! All enemy shields depleted!")
                elif selected_ability == AbilityType.NANO_HEAL_FIELD:
                    player_hp = min(100.0, player_hp + 50.0)
                    print(">> Nanite Healing Field active! (+50 HP)")
                elif selected_ability == AbilityType.CLOAKING:
                    print(">> Optical Cloaking active! Enemies cannot detect you this turn.")
            else:
                print(f">> Ability on cooldown for {ability_cd} turns.")
        elif cmd == "c":
            dist_to_center = player_pos.magnitude()
            if dist_to_center < 30.0:
                territory_progress = min(100.0, territory_progress + 35.0)
                print(f">> Capturing Central Spire... Progress: {territory_progress:.0f}%")
                if territory_progress >= 100.0:
                    print(">> [OBJECTIVE COMPLETE] Central Spire secured by your team!")
            else:
                print(f">> Too far from Central Spire (Distance: {dist_to_center:.1f}m, need < 30m). Move closer to (0, 0).")
        elif cmd == "f":
            if ammo <= 0:
                print(">> Clip empty! Press [r] to reload.")
            else:
                ammo -= 1
                # Target closest enemy
                target = min(active_enemies, key=lambda e: player_pos.distance_to(e["pos"]))
                dist = player_pos.distance_to(target["pos"])
                dmg = 35.0 if selected_weapon == WeaponType.ASSAULT_RIFLE else (80.0 if selected_weapon == WeaponType.PLASMA_SNIPER else 45.0)
                
                # Apply damage
                absorbed = min(target["shield"], dmg)
                target["shield"] -= absorbed
                target["hp"] -= (dmg - absorbed)
                print(f">> Fired at {target['name']}! Dealt {dmg:.0f} damage (Distance: {dist:.1f}m)")

                if target["hp"] <= 0:
                    print(f">> [KILL CONFIRMED] {target['name']} eliminated!")
                    kills += 1
                    score_a += 1

        # Enemy Turn
        if ability_cd > 0:
            ability_cd -= 1

        for e in [e for e in enemies if e["hp"] > 0]:
            dist = player_pos.distance_to(e["pos"])
            if dist < 45.0:
                incoming_dmg = random.uniform(10.0, 20.0)
                absorbed = min(player_shield, incoming_dmg)
                player_shield -= absorbed
                player_hp -= (incoming_dmg - absorbed)
                print(f"   <!> {e['name']} fired back dealing {incoming_dmg:.0f} damage!")

    if player_hp > 0 and len([e for e in enemies if e["hp"] > 0]) == 0:
        print("\n" + "=" * 65)
        print("                 VICTORY! SECTOR LIBERATED")
        print(f"  Total Kills: {kills} | Rating: S-RANK ELITE | Match Won")
        print("=" * 65)
    elif player_hp <= 0:
        print("\n" + "=" * 65)
        print("               DEFEAT: OPERATIVE DOWN")
        print("=" * 65)


if __name__ == "__main__":
    main()
