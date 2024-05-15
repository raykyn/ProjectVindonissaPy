#!/usr/bin/env python3

from typing import TYPE_CHECKING

from vindonissa.events.eventsystem import EventSystem, Event

if TYPE_CHECKING:
    from vindonissa.game_objects.character import Character

import random


def register_yearly_events(character):
    """
    Schedule all potential(!) character events for one year.
    So this pretty much includes all events that are not directly triggered from another event or situation.
    Checking if a character is valid is only done when the event is triggered, unless
    the condition targets an unchangeable characteristic of the character, such as the gender.
    Let's collect allowed conditions here:
    - is_female
    """
    if character.is_female:
        EventSystem.queue_event_randomly(Event(get_pregnant, character))


### LIFECYCLE EVENTS ###

# all probabilities should be considered "per year"
PREGNANCY_CHANCE = 0.25

def get_pregnant(character):
    """
    TODO: Implement bastard children.
    """
    if not character.is_child and character.is_married:
        if random.random() < PREGNANCY_CHANCE and character.is_alive:
            # TODO: character should get a condition => pregnant (might play a role in some events or checks)
            # we queue a subsequent birth event and TODO: potential pregnancy events until the birth
            EventSystem.queue_event(Event(give_birth, character), random.randint(270, 290))


def give_birth(character):
    """
    Gets queued by the get_pregnant event.
    """
    raise NotImplementedError
