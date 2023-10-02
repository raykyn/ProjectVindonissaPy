#!/usr/bin/env python3

from typing import List


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

    @classmethod
    def queue_yearly_event(cls, event, day: int):
        cls.yearly_events[day].append(event)

    @classmethod
    def execute_yearly_events(cls, day: int):
        for event in cls.yearly_events[day]:
            event.execute()
