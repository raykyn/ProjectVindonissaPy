#!/usr/bin/env python3

from typing import List, Dict
from vindonissa.game_objects.cell import Cell


class WorldMap(object):
    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height

        # cells
        self.cells: List[Cell] = []
        self.cells_by_id: Dict[int, Cell] = None
        self.land_cells: List[Cell] = []

        # rivers
        self.rivers = []

    def setup_cells(self):
        self.cells_by_id: Dict[int, Cell] = {cell.id: cell for cell in self.cells}
        self.land_cells: List[Cell] = [cell for cell in self.cells if not cell.is_water]

        # kind of crude way to know which are the border cell
        sorted_x = sorted(self.cells, key=lambda x: x.x)
        sorted_y = sorted(self.cells, key=lambda x: x.y)
        for s in sorted_x[:self.height] + sorted_x[-self.height:] + sorted_y[:self.width] + sorted_y[-self.width:]:
            s.is_border_cell = True

    def get_cell_by_id(self, idx):
        return self.cells_by_id[idx]