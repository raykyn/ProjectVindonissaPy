#!/usr/bin/env python3

import enum
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from vindonissa.game_objects.culture import Culture

class CulturalDiscrimination(enum.Enum):
    Accepted = 1
    Discriminated = 0


class Laws(object):
    def __init__(self):
        pass


class CityLaws(Laws):
    def __init__(self):
        self.culture_discrimination: Dict[Culture, CulturalDiscrimination] = {}