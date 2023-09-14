#!/usr/bin/env python3

import pygame_gui
from session import Session

LEFT_TEXT: pygame_gui.elements.UITextBox = None
RIGHT_TEXT: pygame_gui.elements.UITextBox = None

welcome_message = 'Welcome! Write "new game" to begin a new game or "load game" to load a save game.'

menu_commands = ["help", "new_game"]

def process_command(command):
    LEFT_TEXT.append_html_text("<br>Processing command...")
    out = ""
    if command == "help":
        # TODO: Print all commands with corresponding use.
        out = f"You're in the menu. Available commands are: {', '.join(menu_commands)}"
    elif command == "new game":
        session = Session()
        session.setup()
    else:
        out = "Command was not recognized."
        # TODO: Implement a function which gives suggestions for the meant command

    LEFT_TEXT.append_html_text("<br>" + out)