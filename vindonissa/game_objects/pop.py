#!/usr/bin/env python3

from typing import TYPE_CHECKING, Optional
import enum

if TYPE_CHECKING:
    from vindonissa.game_objects.culture import Culture


class Work (enum.Enum):
    Unassigned = 0
    Farming = 1
    Fishing = 2
    Mining = 3
    Forestry = 4
    Trade = 5
    Artisan = 6

class Pop (object):
    """
    Base class for all pop types.
    """
    def __init__(self, culture, size: int, work: Work = Work.Unassigned, is_urban: bool = False):
        # identifiers
        self.culture: Culture = culture

        # size
        self.size = size

        # work
        self.work: Work = work
        self.is_urban: bool = is_urban

    def __str__(self) -> str:
        return f"Pop of Culture {self.culture} and size {self.size}, working {self.work.name}"  # type: ignore
    
    def __repr__(self) -> str:
        return f"Pop of Culture {self.culture} and size {self.size}, working {self.work.name}"  # type: ignore
    
    def split_off_for_work(self, work: Work):
        """
        Returns a new Pop with identical identifiers (see init),
        but new work type.
        """
        return Pop(self.culture, 0, work=work)
    
    def check_if_equal_but_not_same(self, other: "Pop"):
        """
        Checks if all identifiers are qual between this and other.
        """
        return self.culture == other.culture and self.work == other.work
        