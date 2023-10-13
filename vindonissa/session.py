#!/usr/bin/env python3

import random
from typing import List
#import dill as pickle
import pickle
import sys

from vindonissa.events.eventsystem import EventSystem
from vindonissa.scene import Scene
from vindonissa.util.calendar import Calendar
from game_objects.map import WorldMap
from vindonissa.game_setup import mapgen, citygen, culturegen, popgen, chargen, final_setup

class Session(Scene):
    """
    The Session object holds all information about a game session.
    Such as the map, the characters, the date and time currently in the game
    or events that are queued.
    Saving a game session should be as easy as to binarize this object.
    """
    def __init__(self, main):
        self.main = main
        self.map: WorldMap

        self.calendar = Calendar(main.pygame)

    def setup(self, seed: int = 42) -> None:
        """
        Triggered when a new game is created.
        """
        random.seed(seed)
        # TODO: Update screen every time a step in world generation has finished
        self.map: WorldMap = mapgen.create_worldmap()
        self.main.write_left_text("Finished terrain generation!")
        citygen.generate(self.map)
        self.main.write_left_text("Finished city generation!")
        culturegen.generate(self.map)
        self.main.write_left_text("Finished culture generation!")
        popgen.generate(self.map)
        self.main.write_left_text("Finished population generation!")
        chargen.generate(self.map)
        self.main.write_left_text("Finished character generation!")
        #final_setup.setup(self.map)

    def __getstate__(self):
        """
        Assign which values are pickled!
        Important as we can't pickle modules!
        """
        return (self.map, self.calendar, EventSystem.yearly_events)
    
    def __setstate__(self, state):
        """
        Assign which values are pickled!
        Important as we can't pickle modules!
        """
        self.map, self.calendar, yearly_events = state
        EventSystem.yearly_events = yearly_events

    def load(self, main):
        """
        Called by the menu to link the pygame module to the calendar.
        """
        self.main = main
        self.calendar.pygame = main.pygame
        self.calendar.time_event = main.pygame.event.custom_type()

    def process_command(self, c: str):
        """
        All commands a player can give proactively are collected and executed here.
        """
        command: List[str] = c.split()

        match command[0]:
            case "save":
                sys.setrecursionlimit(9999999)
                if len(command) == 1:
                    self.main.write_left_text("Command was not recognized.")
                    self.main.write_left_text("Were you looking for one of these commands?<br>- save game<br>- save map")
                else:
                    match command[1]:
                        case "game":
                            # TODO: Make this much nicer.
                            if len(command) == 2:
                                self.main.write_left_text("No filename was given, please try again.")
                            else:
                                self.main.write_left_text("Saving your game...")
                                pickle.dump(self, open(f"savegames/{command[2]}.pkl", mode="wb"))
                                self.main.write_left_text("Finished saving...")
                        case "map":
                            # TODO: Make this much nicer.
                            if len(command) == 2:
                                self.main.write_left_text("No filename was given, please try again.")
                            else:
                                self.main.write_left_text("Saving your map...")
                                pickle.dump(self.map, open(f"mapfiles/{command[2]}.pkl", mode="wb"))
                                self.main.write_left_text("Finished saving...")
                        case _:
                            self.main.write_left_text("Command was not recognized.")
                            self.main.write_left_text("Were you looking for one of these commands?<br>- save game<br>- save map")
            case "show_map":
                # only for debug atm as it shuts down the game
                from vindonissa.game_setup.mapviz import draw_map
                draw_map(self.map)
            case _:
                self.main.write_left_text("Command was not recognized.")

    def process_question(self, c: str):
        command: List[str] = c.split()

        match command[0]:
            case "show":
                if len(command) == 1:
                    self.main.write_right_text("Possible categories to show: char, city, culture")
                else:
                    match command[1]:
                        case "char":
                            if len(command) == 2:
                                self.main.write_right_text("Please give name or id of character you're looking for.")
                            else:
                                idx = int(command[2])
                                self.main.write_right_text(self.map.characters[idx].info)
