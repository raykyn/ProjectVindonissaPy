#!/usr/bin/env python3

import math
from typing import List
from vindonissa.game_objects.cell import Cell
from vindonissa.game_objects.city import WayNode, City, Port
from vindonissa.game_objects.map import WorldMap

import random


def traderoute_cost(source: Cell, target: Cell):
    """
    Pathfinding cost function for transport of wares.
    Should heavily favor transport via water and punish 
    higher elevation terrain.
    """
    # entering and leaving water costs a bit more
    if (source.is_water and not target.is_water) or (not source.is_water and target.is_water):
        return 40

    if target in [c for r, c, m in source.river_connections if m == "out"]:
        return 10
    
    # but moving along coasts is fast
    if target.is_water and not target.is_deep_water:
        return 10
    
    # and moving in deep water is a bit slower
    if target.is_water and target.is_deep_water:
        return 20
    
    cost = 20

    if target.elevation_category == 4:
        cost = 1000
    elif target.elevation_category == 3:
        cost = 100
    elif target.elevation_category == 2:
        cost = 30
    elif target.elevation_category == 1:
        cost = 20
    elif target.elevation_category == 0:
        cost = 10
    
    # additional modifiers
    # tree level (-5 to +5 pts for no forests to forests)
    cost += round((target.trees * 10) - 5)

    return cost


def connect_cities(map: WorldMap):
    # improve sea connection finding
    # sea distance between cities should not include
    # embarkement cost!
    for city in map.cities:
        portcounter = 0
        harbors: List[List[Cell]] = []
        for cell in city.terrain:
            if not cell.is_water or cell.is_deep_water:
                continue
            if cell in [c for h in harbors for c in h]:
                # already part of a harbor
                continue
            inside: List[Cell] = []
            map.flood_fill(cell, inside, lambda x: x.is_water and not x.is_deep_water and x.city == cell.city)
            harbors.append(inside)
        
        for harbor in harbors:
            cell = harbor[0]
            port = Port(portcounter, city, cell)
            city.ports.append(port)
            path = map.cell_to_cell_path(city.cell, port.cell, traderoute_cost)
            distance = 0
            for current, next in zip(path[:-1], path[1:]):
                distance += traderoute_cost(current, next)
            city.port_connections.append(distance)
            portcounter += 1

    # we make calculation more efficient by keeping previously
    # calculated paths in memory
    distance_cache = {}
    land_path_cache = {}

    # get a city network for land routes
    for city in map.cities:
        # sort other city by their closeness (luftlinie)
        closest_cities = sorted(map.cities, key=lambda x: math.dist((city.cell.x, city.cell.y), (x.cell.x, x.cell.y)))
        
        tolerance = 4

        for c in closest_cities:
            if c == city:
                continue

            distance = 0
            is_valid = True
            
            if (c.id, city.id) in distance_cache:
                distance = distance_cache[(c.id, city.id)]
                path = land_path_cache[(c.id, city.id)]
            else:
                path = map.cell_to_cell_path(city.cell, c.cell, traderoute_cost, only_land=True)
                if not path:
                    continue
                for current, next in zip(path[:-1], path[1:]):
                    distance += traderoute_cost(current, next)
                    # if any cell is not part of the source or target city,
                    # we cancel the connection
                    if current.city not in [city, c, None]:
                        is_valid = False
                        break
            
            if is_valid:
                city.neighbors.append(c)
                distance_cache[(city.id, c.id)] = distance
                city.land_connections[c.id] = distance
                map.roads.append(path)
                land_path_cache[(city.id, c.id)] = path
            else:
                if tolerance == 0:
                    break
                else:
                    tolerance -= 1

    distance_cache = {}
    sea_path_cache = {}

    for city in map.cities:
        for port in city.ports:
            closest_ports = sorted([p for c in map.cities for p in c.ports], key=lambda x: math.dist((port.cell.x, port.cell.y), (x.cell.x, x.cell.y)))
            
            tolerance = 4

            for p in closest_ports:
                if port == p:
                    continue

                distance = 0
                is_valid = True
                 

                if ((p.city.id, p.id), (city.id, port.id)) in distance_cache:
                    distance = distance_cache[((p.city.id, p.id), (city.id, port.id))]
                    path = sea_path_cache[((p.city.id, p.id), (city.id, port.id))]
                else:
                    path = map.cell_to_cell_path(port.cell, p.cell, traderoute_cost, only_water=True)
                    if not path:
                        continue
                    for current, next in zip(path[:-1], path[1:]):
                        distance += traderoute_cost(current, next)
                        # if any cell is not part of the source or target city,
                        # we cancel the connection
                        if current.city not in [port.city, p.city, None]:
                            is_valid = False
                            break
                if is_valid:
                    port.port_connections.append((p, distance))
                    distance_cache[((city.id, port.id), (p.city.id, p.id))] = distance
                    map.sea_roads.append(path)
                    sea_path_cache[((city.id, port.id), (p.city.id, p.id))] = path
                else:
                    if tolerance == 0:
                        break
                    else:
                        tolerance -= 1

    # calculate pathfinding cost to each city


def generate(map: WorldMap):
    # first phase: place cities randomly, except avoid water cells
    candidate_cells = map.land_cells.copy()
    random.shuffle(candidate_cells)

    # second phase: create proto-traderoutes, weigh city creation along those
    # for each side to each side, we create K trade routes
    border_cells = [
        [c for c in map.cells if c.is_border_cell_north], 
        [c for c in map.cells if c.is_border_cell_east],
        [c for c in map.cells if c.is_border_cell_south],
        [c for c in map.cells if c.is_border_cell_west],
        ]
    for i, sideA in enumerate(border_cells):
        for j, sideB in enumerate(border_cells):
            if i == j:
                continue
            sources = random.sample(sideA, round(len(sideA) * 0.1))
            targets = random.sample(sideB, round(len(sideB) * 0.1))

            for source, target in zip(sources, targets):
                if source.is_water:
                    continue
                path = map.cell_to_cell_path(source, target, cost=traderoute_cost)
                rewarded_neighbors = []  # each coastal cell can only profit once from a route passing on the water before it
                for p in path:
                    p.route_counter += 1
                    if p.is_water:
                        for neighbor in [n for n in p.neighbors if not n.is_water and not n in rewarded_neighbors]:
                            neighbor.route_counter += 1
                            rewarded_neighbors.append(neighbor)

    # third phase: replace the generation only by routes
    # by a general attractiveness of this seed that should
    # also take into account the fertility of the land, etc.

    candidate_cells = sorted(candidate_cells, key=lambda x: x.route_counter, reverse=True)

    map.cities = []
    for cell in candidate_cells:
        if cell.city is not None or any([c.city is not None for c in cell.neighbors]):
            continue
        
        new_city = City(len(map.cities), cell)

        map.cities.append(new_city)

    connect_cities(map)

    return map


if __name__ == "__main__":
    random.seed(42)
    from vindonissa.game_setup import mapgen
    from vindonissa.game_setup.mapviz import draw_map
    map = generate(mapgen.create_worldmap())

    import pickle
    import sys
    sys.setrecursionlimit(100000)
    pickle.dump(map, open("seed_42.pkl", mode="wb"))
    import pickle
    from vindonissa.game_setup.mapviz import draw_map
    #map = pickle.load(open("savetest.pkl", mode="rb"))
    draw_map(map)