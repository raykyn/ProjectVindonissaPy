#!/usr/bin/env python3

from collections import namedtuple

TerrainType = namedtuple('Terrain', [
    'type', 
    'farming', 
    'fishing',
    'mining',
    ])

TERRAIN_TYPES = [
    TerrainType(
        "coast",
        0,
        8000,
        0
    ),
    TerrainType(
        "plains",
        10000,
        0,
        0
    ),
    TerrainType(
        "highlands",
        8000,
        0,
        3000
    ),
    TerrainType(
        "low_mountains",
        6000,
        0,
        5000
    ),
    TerrainType(
        "high_mountains",
        4000,
        0,
        6000
    ),
]

RIVER_BONUS_FISHING = 2000
RIVER_BONUS_FARMING = 1.2