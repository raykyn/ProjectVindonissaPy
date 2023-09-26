#!/usr/bin/env python3

from game_objects.map import WorldMap
from vindonissa.game_setup import mapgen, citygen

class Session(object):
    """
    The Session object holds all information about a game session.
    Such as the map, the characters, the date and time currently in the game
    or events that are queued.
    Saving a game session should be as easy as to binarize this object.
    """
    def __init__(self, left_text):
        self.map: WorldMap = None

        # show stuff to player
        self.left_text = left_text


    def setup(self) -> None:
        """
        Triggered when a new game is created.
        """
        self.map: WorldMap = mapgen.create_worldmap()
        self.left_text.append_html_text("<br>Finished terrain generation!")
        citygen.generate(self.map)
        self.left_text.append_html_text("<br>Finished city generation!")
