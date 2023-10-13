#!/usr/bin/env python3

from vindonissa.game_objects.cell import Cell

def traderoute_cost(source: Cell, target: Cell):
    """
    Pathfinding cost function for transport of wares.
    Should heavily favor transport via water and punish 
    higher elevation terrain.
    """
    # entering and leaving water costs a bit more
    if (source.is_water and not target.is_water) or (not source.is_water and target.is_water):
        return 80

    if target in [c for r, c, m in source.river_connections if m == "out"]:
        return 50
    
    # but moving along coasts is fast
    if target.is_water and not target.is_deep_water:
        return 50
    
    # and moving in deep water is a bit slower
    if target.is_water and target.is_deep_water:
        return 70
    
    cost = 70

    if target.elevation_category == 4:
        cost = 200
    elif target.elevation_category == 3:
        cost = 100
    elif target.elevation_category == 2:
        cost = 80
    elif target.elevation_category == 1:
        cost = 70
    elif target.elevation_category == 0:
        cost = 50
    
    # additional modifiers
    # tree level (-5 to +5 pts for no forests to forests)
    cost += round((target.trees * 10) - 5)

    return cost