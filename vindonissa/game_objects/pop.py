#!/usr/bin/env python3

from vindonissa.game_objects.culture import Culture


class Pop (object):
    """
    Base class for all pop types.
    """
    def __init__(self, culture: Culture, size: int):
        self.culture = culture
        self.size = size

    def __str__(self) -> str:
        return f"Pop of Culture {self.culture} and size {self.size}"