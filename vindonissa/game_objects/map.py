#!/usr/bin/env python3

from typing import List
from vindonissa.game_objects.cell import Cell


class WorldMap(object):
    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self.cells: List[Cell] = []