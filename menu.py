#!/usr/bin/env python3

import pygame
import pygame_gui

LEFT_TEXT: pygame_gui.elements.UITextBox = None
RIGHT_TEXT: pygame_gui.elements.UITextBox = None

welcome_message = 'Welcome! Write "new game" to begin a new game or "load game" to load a save game.'

def process_command(command):
    LEFT_TEXT.append_html_text("<br>Processing command...")