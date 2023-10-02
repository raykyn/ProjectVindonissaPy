#!/usr/bin/env python3

# culture generation
PROVINCES_PER_CULTURE = 6
CULTURES_PER_GROUP = 4
CULTURE_SPREAD_MAXIMUM_SEA_DISTANCE = 200

# character generation
FAMILIES_PER_PROVINCE = 3
MAX_RULER_AGE = 70
MIN_RULER_AGE = 16
GENDER_PREF_PROB_THRESHOLDS = (
    (0.2, 0),
    (0.4, 0.05),
    (0.6, 0.1),
    (0.8, 0.5),
    (1, 0.75)
)