#!/usr/bin/env python3

import random

from game_objects.map import WorldMap
from vindonissa.game_setup import mapgen, citygen, culturegen, popgen, chargen

class Session(object):
    """
    The Session object holds all information about a game session.
    Such as the map, the characters, the date and time currently in the game
    or events that are queued.
    Saving a game session should be as easy as to binarize this object.
    """
    def __init__(self, left_text):
        # show stuff to player
        self.left_text = left_text


    def setup(self, seed: int = 42) -> None:
        """
        Triggered when a new game is created.
        """
        random.seed(seed)
        # TODO: Update screen every time a step in world generation has finished
        self.world_map: WorldMap = mapgen.create_worldmap()
        self.left_text.append_html_text("<br>Finished terrain generation!")
        citygen.generate(self.world_map)
        self.left_text.append_html_text("<br>Finished city generation!")
        culturegen.generate(self.world_map)
        self.left_text.append_html_text("<br>Finished culture generation!")
        popgen.generate(self.world_map)
        self.left_text.append_html_text("<br>Finished population generation!")
        chargen.generate(self.world_map)
        self.left_text.append_html_text("<br>Finished character generation!")

