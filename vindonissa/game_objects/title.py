#!/usr/bin/env python3

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vindonissa.game_objects.character import Character
    from vindonissa.game_objects.laws import Laws, CityLaws
    from vindonissa.game_objects.city import City


class Title(object):
    def __init__(self, id: int, laws):
        self.id = id
        self.laws: Laws = laws


class CityTitle(Title):
    def __init__(self, id: int, city, laws):
        super().__init__(id, laws)
        self.city = city

        self.de_facto_holder: Character
        # self.administrator: Character|None = None  # TODO: make this a proper system

