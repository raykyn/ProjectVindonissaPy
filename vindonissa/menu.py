#!/usr/bin/env python3

import pickle
from scene import Scene
from session import Session

WELCOME_MESSAGE = 'Welcome! Write "new game" to begin a new game or "load game" to load a save game.'



class Menu (Scene):

    def __init__(self, main):
        self.main = main
        self.commands = ["help", "new game"]

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
            self.main.scene = session
        elif command == "continue game":
            # TODO: Load up the newest savegame in the savegame folder
            raise NotImplementedError
        elif command.startswith("load game"):
            command = command.split()
            session: Session = pickle.load(open(f"savegames/{command[2]}.pkl", mode="rb"))
            session.load(self.main)
            self.main.session = session
            self.main.scene = session
        elif command == "load map":
            # TODO: load a binarized map and start a game on it.
            raise NotImplementedError
        else:
            out = "Command was not recognized."
            # TODO: Implement a function which gives suggestions for the meant command

        self.main.write_left_text(out)

    def process_question(self, command: str):
        """
        While in menu, the right side does nothing.
        I should probably deactivate it while in menu.
        """
        return None