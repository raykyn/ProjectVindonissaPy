#!/usr/bin/env python3

import math

from vindonissa.events.eventsystem import EventSystem

MONTHS_ABBR = [
    "Jan.",
    "Feb.",
    "Mar.",
    "Apr.",
    "May",
    "Jun.",
    "Jul.",
    "Aug.",
    "Sep.",
    "Oct.",
    "Nov.",
    "Dec."
]
    

class Calendar(object):
    def __init__(self, pygame):
        self.pygame = pygame
        self.yearday: int = 0  # from 1 to 360
        self.year: int = 1  # from 1 to inf

        self.time_event = self.pygame.event.custom_type()

    def __getstate__(self):
        """
        Assign which values are pickled!
        Important as we can't pickle modules!
        """
        return (self.yearday, self.year)
    
    def __setstate__(self, state):
        """
        Assign which values are pickled!
        Important as we can't pickle modules!
        """
        self.yearday, self.year = state

    def start_timer(self, millis_per_day):
        self.pygame.time.set_timer(self.time_event, millis_per_day)

    def pass_day(self):
        self.yearday += 1

        if self.yearday == 361:
            self.yearday = 1
            self.year += 1
        
        EventSystem.execute_yearly_events(self.yearday-1)
        EventSystem.pop_events()

    @property
    def datestring(self):
        """
        Converts yearday and year to a proper date string.
        """
        day = self.yearday % 30
        if day == 0:
            day = 30
            month = MONTHS_ABBR[math.floor(self.yearday / 30) - 1]
        else:
            month = MONTHS_ABBR[math.floor(self.yearday / 30)]
        return f"{day:02}. {month} {self.year:04}"

