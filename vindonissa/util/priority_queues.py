#!/usr/bin/env python3

from typing import List
from vindonissa.game_objects.cell import Cell
from vindonissa.game_objects.city import WayNode


class CityPriorityQueue (object):
        
    def __init__(self):
        self.list: List[WayNode|None] = []
        self.count = 0
        self.minimum = -1  # -1 indicates no minimum yet

    def enqueue(self, cell: WayNode) -> None:
        self.count += 1
        priority = cell.search_priority
        if self.minimum < 0 or priority < self.minimum:
            self.minimum = priority
        while priority >= len(self.list):
            self.list.append(None)
        cell.next_cell_with_same_prio = self.list[priority]
        self.list[priority] = cell

    def dequeue(self) -> WayNode|None:
        self.count -= 1
        while self.minimum < len(self.list):
            cell = self.list[self.minimum]
            if cell is not None:
                self.list[self.minimum] = cell.next_cell_with_same_prio
                return cell
            self.minimum += 1
        return None
    
    def change(self, cell: WayNode, old_prio: int):
        current = self.list[old_prio]
        if current is not None:
            next_cell = current.next_cell_with_same_prio
        else:
            next_cell = None
        #print("next", next_cell)
        if current == cell:
            self.list[old_prio] = next_cell
        else:
            while next_cell != cell:
                current = next_cell
                if current is None:
                    break
                assert current is not None
                next_cell = current.next_cell_with_same_prio
            else:
                current.next_cell_with_same_prio = cell.next_cell_with_same_prio
        self.enqueue(cell)
        self.count -= 1

    def clear(self):
        self.list.clear()
        self.count = 0
        self.minimum = -1


class CellPriorityQueue (object):
        
    def __init__(self):
        self.list: List[Cell|None] = []
        self.count = 0
        self.minimum = -1  # -1 indicates no minimum yet

    def enqueue(self, cell: Cell) -> None:
        self.count += 1
        priority = cell.search_priority
        if self.minimum < 0 or priority < self.minimum:
            self.minimum = priority
        while priority >= len(self.list):
            self.list.append(None)
        cell.next_cell_with_same_prio = self.list[priority]
        self.list[priority] = cell

    def dequeue(self) -> Cell|None:
        self.count -= 1
        while self.minimum < len(self.list):
            cell = self.list[self.minimum]
            if cell is not None:
                self.list[self.minimum] = cell.next_cell_with_same_prio
                return cell
            self.minimum += 1
        return None
    
    def change(self, cell: Cell, old_prio: int):
        current = self.list[old_prio]
        if current is not None:
            next_cell = current.next_cell_with_same_prio
        else:
            next_cell = None
        #print("next", next_cell)
        if current == cell:
            self.list[old_prio] = next_cell
        else:
            while next_cell != cell:
                current = next_cell
                if current is None:
                    break
                assert current is not None
                next_cell = current.next_cell_with_same_prio
            else:
                current.next_cell_with_same_prio = cell.next_cell_with_same_prio
        self.enqueue(cell)
        self.count -= 1

    def clear(self):
        self.list.clear()
        self.count = 0
        self.minimum = -1