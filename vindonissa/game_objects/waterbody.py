#!/usr/bin/env python3

from vindonissa.game_objects.cell import Cell
from typing import List

class WaterBody(object):
    def __init__(self, cells: List[Cell]):
        self.cells = cells


class Lake(WaterBody):
    """
    A collection of connected water-cells that do not reach the map border.
    """
    def __init__(self, cells):
        super().__init__(cells)


class Ocean(WaterBody):
    """
    A collection of connected water-cells that do reach the map border.
    """
    def __init__(self, cells):
        super().__init__(cells)