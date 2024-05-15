#!/usr/bin/env python3

from typing import List
import random


class Event(object):
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def execute(self):
        self.func(*self.args)


class EventSystem(object):
    """
    EventSystem functions similarly to a static class,
    as there is never an Eventsystem object instantiated.
    Instead, EventSystem can simply be imported into any
    class which need to queue or dequeue or execute events.

    Yearly events are not removed after triggering.
    """
    yearly_events: List[List[Event]] = [[] for _ in range(360)]
    ticking_events: List[List[Event]] = []

    @classmethod
    def queue_yearly_event(cls, event: Event, day: int):
        cls.yearly_events[day].append(event)

    @classmethod
    def dequeue_yearly_event(cls, event: Event, day: int):
        cls.yearly_events[day].remove(event)

    @classmethod
    def execute_yearly_events(cls, day: int):
        for event in cls.yearly_events[day]:
            event.execute()

    @classmethod
    def queue_event_randomly(cls, event: Event):
        cls.queue_event(event, random.randint(1, 360))
            
    @classmethod
    def queue_event(cls, event: Event, ticks: int):
        while len(cls.ticking_events) < ticks:
            cls.ticking_events.append([])
        cls.ticking_events[ticks - 1].append(event)

    @classmethod
    def pop_events(cls):
        events = cls.ticking_events.pop(0)
        print(len(events))
        for event in events:
            event.execute()
