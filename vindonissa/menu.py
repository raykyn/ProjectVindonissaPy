#!/usr/bin/env python3

import pygame_gui
from session import Session

WELCOME_MESSAGE = 'Welcome! Write "new game" to begin a new game or "load game" to load a save game.'



class Menu (object):

    def __init__(self, main):
        self.main = main
        self.commands = ["help", "new_game"]

        main.write_left_text(WELCOME_MESSAGE)

    def process_command(self, command):
        self.main.write_left_text("Processing command...")
        out = ""
        if command == "help":
            # TODO: Print all commands with corresponding use.
            out = f"You're in the menu. Available commands are: {', '.join(self.commands)}"
        elif command == "new game":
            session = Session(self.main)
            session.setup()
            self.main.session = session
        elif command == "continue game":
            # TODO: Load up the newest savegame in the savegame folder
            raise NotImplementedError
        elif command == "load game":
            # TODO: Make a little dialogue
            raise NotImplementedError
        elif command == "load map":
            # TODO: load a binarized map and start a game on it.
            raise NotImplementedError
        else:
            out = "Command was not recognized."
            # TODO: Implement a function which gives suggestions for the meant command

        self.main.write_left_text(out)