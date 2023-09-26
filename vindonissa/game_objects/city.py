#!/usr/bin/env python3

from typing import Dict, List
from vindonissa.game_objects.cell import Cell


class WayNode(object):
    """
    Acts as parent class for cities and ports.
    """
    def __init__(self):
        self.neighbors: List[City] = []  # holds all neighboring cities
        self.land_connections: Dict[int, int] = {}  # keeps track of path cost
        self.sea_connections: Dict[int, int] = {}


class City(WayNode):
    def __init__(self, id: int, cell: Cell):
        super().__init__()

        self.id = id
        self.cell = cell
        self.terrain: List[Cell] = []

        cell.city_center = self
        cell.city = self
        for c in cell.neighbors:
            c.city = self
            self.terrain.append(c)

        # ports and distances to ports
        self.ports: List[Port] = []
        self.port_connections: List[int] = []


class Port(WayNode):
    def __init__(self, id: int, city: City, cell: Cell):
        super().__init__()
        self.id = id
        self.city = city
        self.cell = cell

        self.port_connections: List[tuple[Port, int]] = []
        
