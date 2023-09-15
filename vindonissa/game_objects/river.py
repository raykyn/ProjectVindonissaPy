#!/usr/bin/env python3


from typing import List
from vindonissa.game_objects.cell import Cell


class River(object):
    def __init__(self, origin: Cell):
        self.origin = origin
        self.path: List[Cell] = [origin]

    def __len__(self):
        return len(self.path)