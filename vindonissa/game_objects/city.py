#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Dict, List
from vindonissa.game_objects.laws import CityLaws

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vindonissa.game_objects.cell import Cell
    from vindonissa.game_objects.culture import Culture
    from vindonissa.game_objects.pop import Pop


class WayNode(object):
    """
    Acts as parent class for cities and ports.
    """
    def __init__(self, cell):
        self.cell: Cell = cell

        self.neighbors: List[City] = []  # holds all neighboring cities
        self.land_connections: Dict[int, int] = {}  # keeps track of path cost
        self.sea_connections: Dict[int, int] = {}

        # util attributes
        self.distance = 0
        self.search_heuristic = 0
        self.path_from: WayNode|None = None
        self.next_cell_with_same_prio: WayNode|None = None

    @property
    def search_priority(self) -> int:
        return self.distance + self.search_heuristic
    
    def get_distance(self, other) -> int:
        if type(self) == City:
            if type(other) == Port:
                return 40
            else:
                return self.land_connections[other.id]
        elif type(self) == Port:
            if type(other) == City:
                return 40
            else:
                for p, v in self.port_connections:
                    if p == other:
                        return v
        return 999  # should never be reached
    
@dataclass
class Capacities(object):
    farming = 0
    fishing = 0
    mining = 0
    forestry = 0

    @property
    def food(self):
        return self.farming + self.fishing


class City(WayNode):
    def __init__(self, id: int, cell):
        super().__init__(cell)
        self.id = id
        
        self.terrain: List[Cell] = []

        cell.city_center = self
        cell.city = self
        for c in cell.neighbors:
            c.city = self
            self.terrain.append(c)

        # capacities & pops
        self.capacities = Capacities()
        self.pops: List[Pop] = []

        # ports and distances to ports
        self.ports: List[Port] = []
        self.port_connections: List[int] = []

        # culture and religion
        self.culture: Culture|None = None
        self.laws = CityLaws()

    @property
    def pop_size(self):
        return sum([p.size for p in self.pops])


class Port(WayNode):
    def __init__(self, id: int, city: City, cell):
        super().__init__(cell)
        self.id = id
        self.city = city

        self.port_connections: List[tuple[Port, int]] = []
        
