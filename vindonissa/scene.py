#!/usr/bin/env python3


class Scene(object):
    """
    parent class for the session and menu classes.
    """
    def __init__(self):
        pass

    def process_command(self, command: str):
        pass

    def process_question(self, command: str):
        pass