#!/usr/bin/env python3

from typing import List
import random

from vindonissa.events.eventsystem import EventSystem, Event
from vindonissa.events.character_events import register_yearly_events
from vindonissa.game_objects.family import Family
from vindonissa.game_objects.culture import Culture
from vindonissa.game_objects.title import CityTitle
from vindonissa.game_objects.court import Court

class Character(object):
    def __init__(self, id: int, family: Family, culture: Culture, age: int, is_female: bool, birthday: int|None = None):   
        self.id = id
        self.family = family
        family.members.append(self)
        self.culture = culture
        self.is_female = is_female
        self.__is_alive = True

        # age and health
        self.age = age
        if birthday is None:
            self.birthday = random.randint(0, 359)
        else:
            self.birthday = birthday
        self.birthday_event = Event(self.age_func)
        EventSystem.queue_yearly_event(self.birthday_event, self.birthday)
        self.yearly_events = Event(register_yearly_events, self)
        EventSystem.queue_yearly_event(self.yearly_events, self.birthday)

        # family relations
        self.spouse: Character = None  # type: ignore
        self.father: Character = None  # type: ignore
        self.mother: Character = None  # type: ignore
        self.children: List[Character] = []

        # further relations
        # TODO: Differentiate between "owning" a court and being a member of a court
        self.court: Court|None = None

        # titles and ownership
        self.__holdings: List[CityTitle] = []

    def __str__(self):
        return "Character " + str(self.id)
    
    def __repr__(self):
        return "Character " + str(self.id)
    
    @property
    def is_alive(self):
        return self.__is_alive
    
    def die(self):
        """
        Called when a character dies.
        NOTE: Remember to dequeue all regularly happening events for this character.
        NOTE: Remove character as spouse.
        TODO: Trigger inheritance mechanics.
        """
        self.__is_alive = False
        EventSystem.dequeue_yearly_event(self.birthday_event, self.birthday)
        EventSystem.dequeue_yearly_event(self.yearly_events, self.birthday)

    @property
    def holdings(self):
        """
        To add a holding, use add_holding!
        """
        return tuple(self.__holdings)

    def add_holding(self, new_holding):
        if not self.is_ruler and self.court is None:
            self.court = Court(self)
        self.__holdings.append(new_holding)

    @property
    def is_ruler(self):
        return bool(self.holdings)

    @property
    def is_child(self):
        """
        Could be made more efficient by simply holding this as a variable.
        """
        return self.age < 16
    
    @property
    def is_married(self):
        return True if self.spouse is not None else False
    
    @property
    def siblings(self):
        """
        TODO: Make more efficient by instead updating the sibling information whenever a parent gets another child.
        """
        char_id_to_obj = {}
        if self.mother is not None:
            char_id_to_obj.update({c.id: c for c in self.mother.children})
        if self.father is not None:
            char_id_to_obj.update({c.id: c for c in self.father.children})
        return [c for c in char_id_to_obj.values() if c != self]
    
    def age_func(self):
        self.age += 1
        if self.id == 42:
            print(self.age)

    @property
    def info(self):
        out = ""
        for k, v in self.__dict__.items():
            out += f"<br>{k}: {v}"
        return out