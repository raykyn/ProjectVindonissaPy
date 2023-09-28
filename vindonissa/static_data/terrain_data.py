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
        800,
        0
    ),
    TerrainType(
        "plains",
        1000,
        0,
        0
    ),
    TerrainType(
        "highlands",
        800,
        0,
        300
    ),
    TerrainType(
        "low_mountains",
        600,
        0,
        500
    ),
    TerrainType(
        "high_mountains",
        400,
        0,
        600
    ),
]

RIVER_BONUS_FISHING = 200
RIVER_BONUS_FARMING = 1.2