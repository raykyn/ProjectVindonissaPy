#!/usr/bin/env python3

from collections import defaultdict
import random

from vindonissa.static_data.terrain_data import TERRAIN_TYPES, RIVER_BONUS_FARMING, RIVER_BONUS_FISHING
from vindonissa.game_objects.city import City
from vindonissa.game_objects.map import WorldMap
from vindonissa.game_objects.pop import Pop


def set_initial_capacities(city: City):
    for cell in city.terrain:
        terrain_type = TERRAIN_TYPES[cell.elevation_category]
        farming = (0.5 * terrain_type.farming) + (0.5 * terrain_type.farming * cell.fertility)
        fishing = (0.5 * terrain_type.fishing) + (0.5 * terrain_type.fishing * cell.fertility)
        mining = (0.5 * terrain_type.mining) + (0.5 * terrain_type.mining * cell.ore_density)
        if cell.has_river:
            farming *= RIVER_BONUS_FARMING
            fishing += (RIVER_BONUS_FISHING * cell.fertility)
        city.capacities.farming += farming
        city.capacities.fishing += fishing
        city.capacities.mining += mining
        # TODO: Forestry and how forests impact capacities

    # normalize by terrain size
    city.capacities.farming = city.capacities.farming / len(city.terrain) # type: ignore
    city.capacities.fishing = city.capacities.fishing / len(city.terrain) # type: ignore
    city.capacities.mining = city.capacities.mining / len(city.terrain) # type: ignore


def set_initial_pops(city: City, max_routes: int):
    assert city.culture is not None
    pop_density = 0.2 + 0.2 * (0.5 * (float(city.cell.route_counter) / float(max_routes)) + 0.5 * random.random())  # 0.2 to 0.4 depending on proto trade route value and a bit of randomness
    same_culture = 1
    same_group = 1 - city.culture.traits.xenophobia * 0.5
    other_group = 1 - city.culture.traits.xenophobia

    culture_counter = defaultdict(float)
    culture_counter[city.culture] += same_culture

    for neighbor in city.neighbors:
        assert neighbor.culture is not None
        if city.culture == neighbor.culture:
            value = same_culture
        elif city.culture.group == neighbor.culture.group:
            value = same_group
        else:
            value = other_group
        culture_counter[neighbor.culture] += value

    total_values = sum(culture_counter.values())

    for culture, value in culture_counter.items():
        bonus = 0.4 if culture == city.culture else 0
        share = (value / total_values) * 0.6 + bonus
        pop = Pop(culture, round(city.capacities.food * pop_density * share))
        city.pops.append(pop)


def generate(map: WorldMap):
    most_routes = max([c.cell.route_counter for c in map.cities])
    for city in map.cities:
        set_initial_capacities(city)
        set_initial_pops(city, most_routes)


if __name__ == "__main__":
    random.seed(42)
    import sys
    sys.setrecursionlimit(100000)
    import pickle
    map = pickle.load(open("seed_42_cultures.pkl", mode="rb"))
    generate(map)
    pickle.dump(map, open("seed_42_pops.pkl", mode="wb"))
    from vindonissa.game_setup.mapviz import draw_map
    draw_map(map)