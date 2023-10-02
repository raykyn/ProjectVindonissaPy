#!/usr/bin/env python3

import math
import random
from typing import TYPE_CHECKING, List

from vindonissa.game_objects.character import Character
from vindonissa.game_objects.map import WorldMap
from vindonissa.game_objects.family import Family, Dynasty
from vindonissa.static_data.gamemetrics import FAMILIES_PER_PROVINCE, MAX_RULER_AGE, MIN_RULER_AGE, GENDER_PREF_PROB_THRESHOLDS


def create_family_head(family: Family, map: WorldMap, is_ruler=False):
    assert family.city.culture is not None
    pref_age = round((family.city.culture.traits.ruler_age_preference *
                     (MAX_RULER_AGE - MIN_RULER_AGE)) + MIN_RULER_AGE)
    age = pref_age + random.randint(-5, 10) + random.randint(-5, 10)
    gender_pref = family.city.culture.traits.ruler_gender_preference
    for tr, prob in GENDER_PREF_PROB_THRESHOLDS:
        if gender_pref < tr:
            break
    is_female = True if random.random() < prob else False  # type: ignore
    
    ruler = Character(len(map.characters), family, family.city.culture, age, is_female)
    family.head = ruler

    if is_ruler:
        family.city.title.de_facto_holder = ruler
        ruler.add_holding(family.city.title)
    else:
        family.city.title.de_facto_holder.court.members.append(ruler)
        ruler.court = family.city.title.de_facto_holder.court

    map.characters.append(ruler)
    return ruler
    

def create_spouse_children(head: Character, map: WorldMap):
    if head.is_child:
        return None
    age_diff = head.age - MIN_RULER_AGE
    married_chance = 1 / (1 + math.exp(-0.1 * (age_diff - 12)))
    if random.random() < married_chance:
        # TODO: Set spouse to be of a family present in the city or neighboring province
        spouse = Character(len(map.characters), head.family, head.culture, max(head.age - 3, 16), not head.is_female)
        map.characters.append(spouse)
        head.spouse = spouse
        spouse.spouse = head

        head.court.members.append(spouse)
        spouse.court = head.court

        x = min(spouse.age, 45) - random.randrange(2, 7)
        married_at_age = 16 + random.randint(0, spouse.age - 16)
        while x >= married_at_age:
            child = Character(len(map.characters), head.family, head.culture, x - 16, bool(round(random.random())))
            map.characters.append(child)

            head.children.append(child)
            spouse.children.append(child)
            if head.is_female:
                child.mother = head
                child.father = spouse
            else:
                child.father = head
                child.mother = spouse

            head.court.members.append(child)
            child.court = head.court

            x = x - random.randrange(2, 7)


def create_parent_siblings(head: Character, map: WorldMap):
    """
    We create one dead parent to connect the siblings to the family head.
    """
    parent = Character(len(map.characters), head.family, head.culture, head.age + random.randrange(16, 45), not head.is_female)
    map.characters.append(parent)
    parent.is_alive = False
    parent.children.append(head)
    if parent.is_female:
        head.mother = parent
    else:
        head.father = parent
    
    y = head.age - random.randrange(2, 7)
    while y >= 0 and parent.age - y < 45:
        child = Character(len(map.characters), head.family, head.culture, y, bool(round(random.random())))
        map.characters.append(child)

        parent.children.append(child)
        if parent.is_female:
            child.mother = parent
        else:
            child.father = parent

        head.court.members.append(child)
        child.court = head.court

        create_spouse_children(child, map)

        y = y - random.randrange(2, 7)


def create_initial_family(family: Family, map: WorldMap, is_ruler=False):
    head = create_family_head(family, map, is_ruler)
    create_spouse_children(head, map)
    create_parent_siblings(head, map)


def generate(map: WorldMap):
    """
    For each city, we generate the initial court of characters
    including one character who is the ruler of the city.

    With the current settings we create appr. 30k characters on
    a default sized map (ca. 600 cities). 
    If this brings performance problems, further downsizing should
    be easy to do.
    """
    for city in map.cities:
        for i in range(FAMILIES_PER_PROVINCE):
            dynasty = Dynasty(len(map.dynasties))
            family = Family(len(map.families), dynasty, city)

            map.families.append(family)

            is_ruler = True if i == 0 else False
            create_initial_family(family, map, is_ruler)


if __name__ == "__main__":
    random.seed(42)
    import sys
    sys.setrecursionlimit(100000)
    import pickle
    map = pickle.load(open("seed_42_pops.pkl", mode="rb"))
    generate(map)
    from vindonissa.events.eventsystem import EventSystem
    for day in EventSystem.yearly_events:
        print(len(day))
    
    #from vindonissa.game_setup.mapviz import draw_map
    #draw_map(map)