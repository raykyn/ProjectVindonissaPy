#!/usr/bin/env python3

import math
from typing import List, Dict

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vindonissa.game_objects.waterbody import Ocean, Lake
    from vindonissa.game_objects.river import River
    from vindonissa.game_objects.city import City


class Cell (object):
    def __init__(self, id: int, x: float, y: float, elevation: float, is_water: bool, coords: List[List[float]], elevation_category: int, treelevel: float):
        self.id = id
        self.x = x
        self.y = y
        self.elevation = elevation
        self.coords = coords
        self.elevation_category = elevation_category
        self.vertices = set()
        self.trees: float = treelevel

        # water stuff
        self.is_water = is_water
        self.is_deep_water = True if is_water else False  # does not border a land cell
        self.is_coastal = False  # borders water as land cell
        self.water_body: Ocean|Lake|None = None

        # city info
        self.city_center: City|None = None
        self.city: City|None = None

        # Is border cell?
        self.is_border_cell = False
        self.is_border_cell_north = False
        self.is_border_cell_east = False
        self.is_border_cell_south = False
        self.is_border_cell_west = False

        # Neighboring cell information
        self.neighbors: List[Cell] = []
        self.neighbor_directions: Dict[Cell, float]|None = None
        
        # river info
        self.river_connections: List[tuple[River, Cell, str]] = []

        # some other util info
        self.route_counter = 0

        # util attributes
        self.distance = 0
        self.search_heuristic = 0
        self.path_from: Cell|None = None
        self.next_cell_with_same_prio: Cell|None = None

    @property
    def search_priority(self) -> int:
        return self.distance + self.search_heuristic

    @property
    def has_river(self) -> bool:
        """
        Check if the cell has any incoming or outgoing rivers.
        """
        return bool(self.river_connections)

    def add_neighbor(self, cell):
        self.neighbors.append(cell)
        assert self.neighbor_directions is not None
        self.neighbor_directions[cell] = self.get_direction(cell)

    def get_direction(self, cell):
        """
        Get the direction of the other cell in a 360° system relative to this cell.
        """
        return math.atan2(cell.y - self.y, cell.x - self.x) * (180 / math.pi)
    
    def __str__(self):
        return "Cell " + str(self.id)
    
    def __repr__(self):
        return "Cell " + str(self.id)