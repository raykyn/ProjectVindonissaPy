#!/usr/bin/env python3

import math
from typing import List, Dict

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vindonissa.game_objects.river import River

class Cell (object):
    def __init__(self, id: int, x: float, y: float, elevation: float, is_water: bool, coords: List[List[float]], elevation_category: int):
        self.id = id
        self.x = x
        self.y = y
        self.elevation = elevation
        self.is_water = is_water
        self.coords = coords
        self.elevation_category = elevation_category
        self.vertices = set()

        # Is border cell?
        self.is_border_cell = False

        # Neighboring cell information
        self.neighbors: List[Cell] = []
        self.neighbor_directions: Dict[Cell, int] = None
        # 0 is incoming, 1 is outgoing
        self.river_connections: List[tuple[River, Cell, str]] = []

    @property
    def has_river(self) -> bool:
        """
        Check if the cell has any incoming or outgoing rivers.
        """
        return bool(self.river_connections)

    def add_neighbor(self, cell):
        self.neighbors.append(cell)
        self.neighbor_directions[cell] = self.get_direction(cell)

    def get_direction(self, cell):
        """
        Get the direction of the other cell in a 360° system relative to this cell.
        """
        return math.atan2(cell.y - self.y, cell.x - self.x) * (180 / math.pi)