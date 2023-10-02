#!/usr/bin/env python3

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from vindonissa.game_objects.city import City
    from vindonissa.game_objects.character import Character


class Dynasty(object):
    def __init__(self, id: int):
        self.id = id
        self.main_line: Family|None = None


class Family(object):
    def __init__(self, id: int, dynasty: Dynasty|None, city):
        self.id = id
        self.dynasty = dynasty
        self.city: City = city

        self.head: Character|None = None
        self.members: List[Character] = []
