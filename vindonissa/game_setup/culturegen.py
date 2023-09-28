#!/usr/bin/env python3

import math
import random
from typing import Dict, List
from opensimplex import OpenSimplex

from vindonissa.static_data import gamemetrics
from vindonissa.game_objects.map import WorldMap
from vindonissa.game_objects.culture import Culture, CultureGroup
from vindonissa.game_objects.city import City
from vindonissa.game_objects.laws import CulturalDiscrimination



def create_culture_area(map: WorldMap):
    num_cultures = round(len(map.cities) / gamemetrics.PROVINCES_PER_CULTURE)
    
    candidates = map.cities.copy()

    seeds: List[City] = []
    while len(candidates) > 0 and len(seeds) < num_cultures:
        current = random.choice(candidates)
        seeds.append(current)
        candidates.remove(current)
        for n in current.neighbors:
            if n in candidates:
                candidates.remove(n)
    
    cultures = []
    for i, seed in enumerate(seeds):
        culture = Culture(i, seed)
        cultures.append(culture)
        seed.culture = culture

    seed_to_city_distances = {}
    for i, seed in enumerate(seeds):
        for city in map.cities:
            if city.culture is not None:
                continue
            if math.dist((seed.cell.x, seed.cell.y), (city.cell.x, city.cell.y)) > 20:
                # this should make the program make many less calculations
                # for the actual game, we could set this very high, as loading time there will be less relevant
                continue
            dist = map.city_to_city_dist(seed, city)
            if dist is None:
                print(seed.id, city.id)
            else:
                seed_to_city_distances[(i, city.id)] = dist

    seed_to_city_distances = sorted(seed_to_city_distances.items(), key=lambda x: x[1])
    already_processed = set()
    for (seed_idx, city_id), dist in seed_to_city_distances:
        if city_id in already_processed:
            continue
        map.cities[city_id].culture = cultures[seed_idx]
        already_processed.add(city_id)

    map.cultures = cultures
    
    return cultures


def get_trait_sample(noise_seed: int, seed: City) -> float:
    noise = OpenSimplex(seed=noise_seed)

    freq = 1
    sample = noise.noise2d(freq * seed.cell.x, freq * seed.cell.y)

    # press into 0 to 1 range
    sample += 1
    sample *= 0.5

    return sample


def assign_culture_traits(cultures: List[Culture]):
    noise_seeds = [
        random.randint(0, 100000),
        random.randint(0, 100000),
        random.randint(0, 100000)
    ]
    for culture in cultures:
        seed = culture.seed
        culture.traits.xenophobia = get_trait_sample(noise_seeds[0], seed)
        culture.traits.ruler_age_preference = get_trait_sample(noise_seeds[1], seed)
        culture.traits.ruler_gender_preference = get_trait_sample(noise_seeds[2], seed)


def assign_culture_groups(cultures: List[Culture], map: WorldMap):
    num_culture_groups = round(len(cultures) / gamemetrics.CULTURES_PER_GROUP)

    seeds = random.sample(cultures, num_culture_groups)

    distances: Dict[tuple[int, int], int] = {} # type: ignore
    for cultureA in seeds:
        for cultureB in cultures:
            if cultureA == cultureB:
                continue
            distance = map.city_to_city_dist(cultureA.seed, cultureB.seed)
            distances[(cultureA.id, cultureB.id)] = distance # type: ignore

    distances: List[tuple[tuple[int, int], int]] = sorted(distances.items(), key=lambda x: x[1]) # type: ignore

    culture_groups = []
    for i, seed in enumerate(seeds):
        group = CultureGroup(i, seed.seed)
        group.members.append(seed)
        seed.group = group
        culture_groups.append(group)

    for (cult_a_id, cult_b_id), dist in distances:
        c = cultures[cult_b_id]
        if c.group is not None:
            continue
        cg = cultures[cult_a_id].group
        assert cg is not None
        c.group = cg
        cg.members.append(c)

    map.culture_groups = culture_groups


def set_discrimination_law(map: WorldMap):
    for city in map.cities:
        assert city.culture is not None
        xenophobia: float = city.culture.traits.xenophobia
        if xenophobia < 0.2:
            same_group = CulturalDiscrimination.Accepted
            other_group = CulturalDiscrimination.Accepted
        elif xenophobia < 0.4:
            same_group = CulturalDiscrimination.Accepted
            other_group = CulturalDiscrimination.Discriminated
        else:
            same_group = CulturalDiscrimination.Discriminated
            other_group = CulturalDiscrimination.Discriminated

        for culture in map.cultures:
            if culture == city.culture:
                city.laws.culture_discrimination[culture] = CulturalDiscrimination.Accepted
            elif culture.group == city.culture.group:
                city.laws.culture_discrimination[culture] = same_group
            else:
                city.laws.culture_discrimination[culture] = other_group


def set_initial_laws(map: WorldMap):
    set_discrimination_law(map)



def generate(map: WorldMap):
    cultures = create_culture_area(map)
    assign_culture_traits(cultures)
    assign_culture_groups(cultures, map)
    set_initial_laws(map)



if __name__ == "__main__":
    random.seed(42)
    import sys
    sys.setrecursionlimit(100000)
    import pickle
    map = pickle.load(open("seed_42.pkl", mode="rb"))
    generate(map)
    pickle.dump(map, open("seed_42_cultures.pkl", mode="wb"))
    from vindonissa.game_setup.mapviz import draw_map
    draw_map(map)