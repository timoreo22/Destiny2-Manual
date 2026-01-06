from typing import Optional, Set
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value
from BaseClasses import MultiWorld, CollectionState

import re


# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def overfishedAnywhere(world: World, state: CollectionState, player: int):
    """Has the player collected all fish from any fishing log?"""
    for cat, items in world.item_name_groups:
        if cat.endswith("Fishing Log") and state.has_all(items, player):
            return True
    return False


# You can also pass an argument to your function, like {function_name(15)}
# Note that all arguments are strings, so you'll need to convert them to ints if you want to do math.
def anyClassLevel(state: CollectionState, player: int, level: str):
    """Has the player reached the given level in any class?"""
    for item in ["Figher Level", "Black Belt Level", "Thief Level", "Red Mage Level", "White Mage Level",
                 "Black Mage Level"]:
        if state.count(item, player) >= int(level):
            return True
    return False


# You can also return a string from your function, and it will be evaluated as a requires string.
def requiresMelee():
    """Returns a requires string that checks if the player has unlocked the tank."""
    return "|Figher Level:15| or |Black Belt Level:15| or |Thief Level:15|"


def goalAmount(world: World, state: CollectionState, player: int):
    return f"|Cleared Dungeon:{world.options.clears_required_for_victory.value}|"


def requiresDpsAndRoam(world: World, state: CollectionState, player: int):
    # Needs one slot with roam and one slot with dps, each slot can be overriden by a valid option
    kinetic: Set[str] = world.item_name_groups.get("Kinetic Weapons", set())
    energy: Set[str] = world.item_name_groups.get("Energy Weapons", set())
    power: Set[str] = world.item_name_groups.get("Power Weapons", set())
    exotic: Set[str] = world.item_name_groups.get("Exotic Weapons", set())
    dps: Set[str] = world.item_name_groups.get("DPS Weapons", set())
    roam: Set[str] = world.item_name_groups.get("Roam Weapons", set())

    dps_exotic: int = 0b111
    roam_exotic: int = 0b111
    dps_options: int = 0b000
    roam_options: int = 0b000

    def has_solution():
        row0 = (-((dps_options >> 0) & 1) & roam_options)
        row1 = (-((dps_options >> 1) & 1) & roam_options)
        row2 = (-((dps_options >> 2) & 1) & roam_options)

        XY = row0 | (row1 << 3) | (row2 << 6)  # 9-bit matrix: row i in bits 3*i..3*i+2

        f0 = (-((dps_exotic >> 0) & 1) & roam_exotic)
        f1 = (-((dps_exotic >> 1) & 1) & roam_exotic)
        f2 = (-((dps_exotic >> 2) & 1) & roam_exotic)
        F = f0 | (f1 << 3) | (f2 << 6)

        allowed = XY & (~F & 0x1FF)  # remove overlapping exotics
        # clear diagonal bits (positions 0,4,8) because i must != j
        allowed &= 0b011101110

        return allowed != 0

    for item in state.prog_items[player].keys():
        if item in dps:
            is_legendary = item not in exotic
            if item in kinetic:
                dps_options |= 0b001
                if is_legendary:
                    dps_exotic &= 0b110
            if item in energy:
                dps_options |= 0b010
                if is_legendary:
                    dps_exotic &= 0b101
            if item in power:
                dps_options |= 0b100
                if is_legendary:
                    dps_exotic &= 0b011
            if has_solution():
                return True
        elif item in roam:
            is_legendary = item not in exotic
            if item in kinetic:
                roam_options |= 0b001
                if is_legendary:
                    roam_exotic &= 0b110
            if item in energy:
                roam_options |= 0b010
                if is_legendary:
                    roam_exotic &= 0b101
            if item in power:
                roam_options |= 0b100
                if is_legendary:
                    roam_exotic &= 0b011
            if has_solution():
                return True
    return False
