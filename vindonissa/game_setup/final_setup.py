#!/usr/bin/env python3

from typing import TYPE_CHECKING

from vindonissa.game_objects.map import WorldMap


def initialize_cities(map: WorldMap):
    """
    Calculate initial pop assignments for all cities
    """
    for city in map.cities:
        city.set_inital_values()


def setup(map: WorldMap):
    """
    Perform the final setup steps where a lot of the game objects interact.
    """

    initialize_cities(map)