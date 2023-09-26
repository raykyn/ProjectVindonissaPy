#!/usr/bin/env python3

import math
from typing import List, Dict
import sys

from vindonissa.game_objects.cell import Cell
from vindonissa.util.priority_queues import CellPriorityQueue
from vindonissa.game_objects.river import River
from vindonissa.game_objects.city import City
from vindonissa.game_objects.waterbody import Lake, Ocean


SEARCH_MAX_DISTANCE = 9999999


class WorldMap(object):
    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        sys.setrecursionlimit(width * height)

        # cells
        self.cells: List[Cell] = []
        self.cells_by_id: Dict[int, Cell] = None
        self.land_cells: List[Cell] = []

        # objects(?)
        self.rivers: List[River] = []
        self.cities: List[City] = []

        # only visuals
        self.roads: List[List[Cell]] = []
        self.sea_roads: List[List[Cell]] = []

        # pathfinding
        self.cell_priority_queue: CellPriorityQueue = CellPriorityQueue() 

    def setup_cells(self):
        self.cells_by_id: Dict[int, Cell] = {cell.id: cell for cell in self.cells}
        self.land_cells: List[Cell] = [cell for cell in self.cells if not cell.is_water]

        # kind of crude way to know which are the border cell
        sorted_x = sorted(self.cells, key=lambda x: x.x)
        sorted_y = sorted(self.cells, key=lambda x: x.y)

        for s in sorted_x[:self.height]:
            s.is_border_cell = True
            s.is_border_cell_west = True

        for s in sorted_x[-self.height:]:
            s.is_border_cell = True
            s.is_border_cell_east = True

        for s in sorted_y[:self.width]:
            s.is_border_cell = True
            s.is_border_cell_north = True

        for s in sorted_y[-self.width:]:
            s.is_border_cell = True
            s.is_border_cell_south = True

    def flood_fill(self, cell: Cell, inside: List[Cell], condition):
        """
        Return all cells that are connected with this cell.
        Inside holds all cells that were already processed.
        Condition is a function that a cell must return
        True for to be added to the fill.
        """
        inside.append(cell)
        for neighbor in cell.neighbors:
            if neighbor in inside:
                continue
            if condition(neighbor):
                self.flood_fill(neighbor, inside, condition)

    def setup_cells2(self):
        """
        Doing some modifications to cells after assigning neighbors.
        """

        # if any cells do not have neighbors (are disconnected, they are deleted)
        for c in self.cells.copy():
            if len(c.neighbors) == 0:
                self.cells.remove(c)
                if not c.is_water:
                    self.land_cells.remove(c)
                del self.cells_by_id[c.id]

        # for all water cells determine which are coastal,
        # and which are deep water, also set all coastal cells as such
        for cell in self.cells:
            if not cell.is_water:
                continue
            for neighbor in cell.neighbors:
                if not neighbor.is_water:
                    cell.is_deep_water = False
                    neighbor.is_coastal = True

        # setup which cells are oceans and lakes and connected to each other
        for cell in self.cells:
            if not cell.is_water:
                continue
            if cell.water_body is not None:
                continue
            inside: List[Cell] = []
            self.flood_fill(cell, inside, lambda x: x.is_water)
            if any([c.is_border_cell for c in inside]):
                wb = Ocean(inside)
            else:
                wb = Lake(inside)
            for cell in inside:
                cell.water_body = wb

    def get_cell_by_id(self, idx):
        return self.cells_by_id[idx]
    
    def cell_to_cell_path(self, source: Cell, target: Cell, cost, only_land=False, only_water=False) -> List[Cell]:
        distance = 0
        path = []

        self.cell_priority_queue.clear()

        for cell in self.cells:
            cell.distance = SEARCH_MAX_DISTANCE
        
        source.distance = 0
        self.cell_priority_queue.enqueue(source)
        while self.cell_priority_queue.count > 0:
            current = self.cell_priority_queue.dequeue()
            
            # end condition
            if current == target:
                while current != source:
                    path.append(current)
                    assert current is not None
                    current = current.path_from
                path.append(current)
                break

            assert current is not None
            for neighbor in current.neighbors:
                assert neighbor is not None
                if only_land and neighbor.is_water:
                    continue
                elif only_water and not neighbor.is_water:
                    continue
                distance = current.distance
                distance += cost(current, neighbor)
                if neighbor.distance == SEARCH_MAX_DISTANCE:
                    neighbor.distance = distance
                    neighbor.path_from = current
                    neighbor.search_heuristic = round(math.dist((neighbor.x, neighbor.y), (target.x, target.y)) * 1)
                    self.cell_priority_queue.enqueue(neighbor)
                elif distance < neighbor.distance:
                    old_prio = neighbor.search_priority
                    neighbor.distance = distance
                    neighbor.path_from = current
                    self.cell_priority_queue.change(neighbor, old_prio)

        return list(reversed(path))
