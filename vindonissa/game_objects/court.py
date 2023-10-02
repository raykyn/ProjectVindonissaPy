#!/usr/bin/env python3

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from vindonissa.game_objects.character import Character


class Court (object):
    """
    A court consists of three kinds of characters:
    a) the ruler
    b) the members, people who are sworn to the ruler and live there when not on missions.
    c) the guests, people who are there for missions or other visits.

    I make this a fully fleshed out class because I believe there
    might be a lot of helpful functions that can be added here.
    """
    def __init__(self, ruler):
        self.ruler: Character = ruler
        self.members: List[Character] = []
        self.guests: List[Character] = []
