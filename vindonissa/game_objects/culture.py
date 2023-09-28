#!/usr/bin/env python3

from dataclasses import dataclass
import random
from typing import Dict, List

from vindonissa.game_objects.city import City


class CultureGroup (object):
    def __init__(self, id: int, seed: City):
        self.id = id
        self.seed = seed
        self.color: tuple[int, int, int] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.members: List[Culture] = []


@dataclass
class Traits:
    xenophobia: float =  0
    ruler_age_preference: float = 0
    ruler_gender_preference: float = 0


class Culture (object):
    def __init__(self, id: int, seed: City):
        self.id = id
        self.seed = seed
        self.color: tuple[int, int, int] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.group: CultureGroup|None = None

        self.traits: Traits = Traits()