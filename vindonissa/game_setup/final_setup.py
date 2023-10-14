#!/usr/bin/env python3

import math
from typing import TYPE_CHECKING
import time

from vindonissa.game_objects.map import WorldMap
from vindonissa.game_objects.city import City, Port, WayNode
from vindonissa.static_data.movement_costs import traderoute_cost
from vindonissa.static_data.gamemetrics import TRADE_VALUE_TO_CAPACITY_RATE

def initialize_cities(map: WorldMap):
    """
    Calculate initial pop assignments for all cities
    """
    start_time = time.time()
    for city in map.cities:
        city.set_inital_values()
    end_time = time.time()
    print("initial setup:", end_time - start_time)

def find_routes(current: WayNode, distance, paths, curr_path):
    if curr_path:
        prev_node = curr_path[-1]
    else:
        prev_node = None
    
    curr_path.append(current)  # Append the current node to the path
    
    assert current is not None
    if type(current) == City:
        neighbors = current.neighbors + current.ports
        costs = list(current.land_connections.values()) + current.port_connections
        assert len(neighbors) == len(costs)
    elif type(current) == Port:
        neighbors = [p for p, v in current.port_connections] + [current.city]
        costs = [v for p, v in current.port_connections] + [80]  # TODO: get distance to city also as an information to the port
        assert len(neighbors) == len(costs)
    else:
        raise ValueError

    found_neighbor = False
    for neighbor, cost in zip(neighbors, costs):
        if cost > distance:
            continue
        if neighbor in curr_path:
            continue
        if prev_node is not None and type(prev_node) != Port and math.dist((curr_path[0].cell.x, curr_path[0].cell.y), (prev_node.cell.x, prev_node.cell.y)) > math.dist((curr_path[0].cell.x, curr_path[0].cell.y), (neighbor.cell.x, neighbor.cell.y)):
            continue
        find_routes(neighbor, distance - cost, paths, curr_path.copy())
        found_neighbor = True
    
    if not found_neighbor:
        paths.append([c for c in curr_path if type(c) == City])

def create_traderoutes(map: WorldMap):
    import sys
    
    for city in map.cities:
        routes = []
        find_routes(city, 1000, routes, [])
        city.potential_traderoutes = routes

def assign_best_routes(map: WorldMap):
    """
    For each city, make them choose their most valuable route. 
    Each other city on that route profits from that as well.
    """
    start_time = time.time()
    create_traderoutes_new(map)

    for city in map.cities:
        city.capacities.set_new_capacity_maximum(city.capacities.trade, round(city.traderoute_wealth * TRADE_VALUE_TO_CAPACITY_RATE))

    for city in map.cities:
        #print("ASSIGN")
        city.update_pop_assignments(disable_cap=True)
        #print("Total:", end_time - start_time)

    end_time = time.time()
    print("one iter:", end_time-start_time)

def create_trade_endnodes(map: WorldMap):
    endpoints = []  # list of pairs

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
            sources = random.sample(sideA, round(len(sideA) * 0.2))
            targets = random.sample(sideB, round(len(sideB) * 0.2))

            for source, target in zip(sources, targets):
                if source.is_water:
                    continue
                first = map.get_closest_city(source, traderoute_cost)
                last = map.get_closest_city(target, traderoute_cost)

                endpoints.append((first, last))

    map.trade_endpoints = endpoints

def create_traderoutes_new(map: WorldMap):
    """
    New try: Similar to proto-traderoutes,
    we choose k starting points in the west and l starting points in the north.
    We run them to the east and south.
    A city gets trade capacity according to its closest neighbors on the route.
    The route chooses a path dictated by shortest distance and max wealth on the route.
    To get a bit more varience we might reduce value of cities according to how
    many routes already flow through.
    """
    # reset citys traderoute infos
    for city in map.cities:
        city.traderoute_counter = 0
        city.traderoute_wealth = 0

    routes = []
    for first, last in map.trade_endpoints:
        route = map.city_to_city_path(first, last, apply_wealth_modifier=True)  # type: ignore
        routes.append(route)
        for k, city in enumerate(route):
            l = k
            total_trade_wealth = 0
            # iterate previous cities
            iterations = 0
            while iterations < 3:
                if l < 0:
                    break
                prev_city = route[l]
                if type(prev_city) == Port:
                    if prev_city.city not in route:
                        total_trade_wealth += prev_city.city.wealth_no_trade
                    else:
                        iterations -= 1
                elif type(prev_city) == City:
                    total_trade_wealth += prev_city.wealth_no_trade
                l -= 1
                iterations += 1
            # iterate following cities
            l = k
            iterations = 0
            while iterations < 3:
                if l >= len(route):
                    break
                next_city = route[l]
                if type(next_city) == Port:
                    if next_city.city not in route:
                        total_trade_wealth += next_city.city.wealth_no_trade
                    else:
                        l += 1
                elif type(next_city) == City:
                    total_trade_wealth += next_city.wealth_no_trade
                l += 1
                iterations += 1

            if type(city) == Port:
                if city.city not in route:
                    city.city.traderoute_counter += 1
                    city.city.traderoute_wealth += total_trade_wealth
            elif type(city) == City:
                city.traderoute_counter += 1
                city.traderoute_wealth += total_trade_wealth
    map.traderoutes = routes

def setup(map: WorldMap):
    """
    Perform the final setup steps where a lot of the game objects interact.
    """
    print("SETUP!")

    initialize_cities(map)
    create_trade_endnodes(map)
    #start_time = time.time() 
    #create_traderoutes_new(map)
    #end_time = time.time()
    #execution_time = end_time - start_time
    #print(execution_time)
    for _ in range(10):
        assign_best_routes(map)


if __name__ == "__main__":
    import random
    random.seed(42)
    import pickle
    import sys
    sys.setrecursionlimit(9999999)
    map = pickle.load(open("mapfiles/test_new_values.pkl", mode="rb"))
    setup(map)
    from vindonissa.game_setup.mapviz import draw_map
    draw_map(map)