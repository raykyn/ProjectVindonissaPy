#!/usr/bin/env python3

from game_objects.map import WorldMap
from game_setup import mapgen

class Session(object):
    """
    The Session object holds all information about a game session.
    Such as the map, the characters, the date and time currently in the game
    or events that are queued.
    Saving a game session should be as easy as to binarize this object.
    """
    def __init__(self):
        self.map: WorldMap = None

    def setup(self) -> None:
        """
        Triggered when a new game is created.
        """
        self.map: WorldMap = mapgen.create_worldmap()