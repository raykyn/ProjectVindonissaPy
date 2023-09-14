#!/usr/bin/env python3


from typing import List


class Cell (object):
    def __init__(self, x: float, y: float, elevation: float, is_water: bool, coords: List[List[float]], elevation_category: int):
        self.x = x
        self.y = y
        self.elevation = elevation
        self.is_water = is_water
        self.coords = coords
        self.elevation_category = elevation_category