#!/usr/bin/env python3

import math
import pygame
from typing import List
from collections import Counter

from vindonissa.game_objects.city import City
from vindonissa.game_objects.cell import Cell
from vindonissa.game_objects.map import WorldMap


BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
SEA = (89, 89, 166)
LAND = (132, 191, 148)
LAND2 = (128, 153, 102)
LAND3 = (101, 117, 105)
GREY = (122, 130, 124)
YELLOW = (255, 255, 0)
ROAD = (175, 150, 125)

GRIDSIZE = 10


def edgesArountPoint(delaunay, start):
    result = []
    incoming = start  #?
    while True:
        result.append(incoming)
        outgoing = nextHalfedge(incoming)
        incoming = delaunay.halfedges[outgoing]
        if incoming == -1 or incoming == start :
            break
    return result


def triangleOfEdge(e):
    return math.floor(e/3)


def nextHalfedge(e):
    return e - 2 if e % 3 == 2 else e + 1


def biomeColor(r, elevation, moisture):
    e = (elevation[r] - 0.5) * 2
    m = moisture[r]
    if e < 0:
        r = 48 + 48 * e
        g = 64 + 64 * e
        b = 127 + 127 * e
    else:
        m = m * (1 - e)
        e = e**4
        r = 210 - 100 * m
        g = 185 - 45 * m
        b = 139 - 45 * m
        r = 255 * e + r * (1-e)
        g = 255 * e + g * (1-e)
        b = 255 * e + b * (1-e)
    return (r, g, b)


def heightColor(e):
    if e < 0.2:
        return SEA
    color = max(0, min(255, int(255 * e)))
    return (color, color, color)


def heightColorByCell(cell):
    if cell.is_water:
        return SEA
    color = max(0, min(255, int(255 * cell.elevation)))
    return (color, color, color)


def heightColorByCategory(cell):
    if cell.elevation_category == 0:
        return SEA
    elif cell.elevation_category == 1:
        return LAND
    elif cell.elevation_category == 2:
        return LAND2
    elif cell.elevation_category == 3:
        return LAND3
    elif cell.elevation_category >= 4:
        return GREY


def drawCellColors(screen, gridsize, triangles, numEdges, centers, delaunay, elevation, moisture):
    seen = set()
    for e in range(numEdges):
        r = triangles[nextHalfedge(e)]
        if r not in seen:
            seen.add(r)
            vertices = edgesArountPoint(delaunay, e)
            if len(vertices) < 3:
                continue
            vertices = [centers[triangleOfEdge(x)] for x in vertices]
            #print(vertices)
            coordinates = [[vertices[0]["x"]*gridsize, vertices[0]["y"]*gridsize]]
            for i in range(1, len(vertices)):
                coordinates.append([vertices[i]["x"]*gridsize, vertices[i]["y"]*gridsize])
            #pygame.draw.polygon(screen, biomeColor(r, elevation, moisture), coordinates)
            pygame.draw.polygon(screen, heightColor(elevation[r]), coordinates)


def drawCellColors2(screen, gridsize, cells):
    for cell in cells:
        #pygame.draw.polygon(screen, heightColorByCell(cell), [(x * gridsize, y * gridsize) for x, y in cell.coords])
        pygame.draw.polygon(screen, heightColorByCategory(cell), [(x * gridsize, y * gridsize) for x, y in cell.coords])  # type: ignore


def drawPoints(canvas, points):
    for point in points:
        x = point[0]
        y = point[1]
        pygame.draw.circle(
            canvas,
            RED,
            [x*GRIDSIZE, y*GRIDSIZE],
            1
        )
    
def drawPoint(canvas, point, gridsize, color=RED, size=5):
    x = point[0]
    y = point[1]
    pygame.draw.circle(
        canvas,
        color,
        [x*gridsize, y*gridsize],
        size
    )

def drawTrees(canvas, cells):
    for cell in cells:
        pygame.draw.circle(
            canvas,
            (0, 125, 0),
            [cell.x*GRIDSIZE, cell.y*GRIDSIZE],
            cell.trees * 5
        )


def drawRiver(canvas, river, color=BLUE):
    pygame.draw.lines(canvas, color, False, [(c.x*GRIDSIZE, c.y*GRIDSIZE) for c in river.path])


def drawCities(canvas, cells: List[Cell]):
    for cell in cells:
        if cell.city_center is not None:
            pygame.draw.circle(
                canvas,
                BLACK,
                [cell.x*GRIDSIZE, cell.y*GRIDSIZE],
                max(round(cell.route_counter * 0.5), 1)
            )

def drawPath(canvas, path, color):
    for cell in path:
        pygame.draw.circle(
            canvas,
            color,
            [cell.x*GRIDSIZE, cell.y*GRIDSIZE],
            3
        )


def test_pathfinding_cost(source: Cell, target: Cell):
    if target in [c for r, c, m in source.river_connections if m == "out"]:
        return 10
    
    # entering and leaving water costs a bit more
    if (source.is_water and not target.is_water) or (not source.is_water and target.is_water):
        return 40
    
    # but moving along coasts is fast
    if target.is_water and not target.is_deep_water:
        return 10
    
    # and moving in deep water is a bit slower
    if target.is_water and target.is_deep_water:
        return 20

    if target.elevation_category == 4:
        return 1000
    elif target.elevation_category == 3:
        return 100
    elif target.elevation_category == 2:
        return 30
    elif target.elevation_category == 1:
        return 20
    elif target.elevation_category == 0:
        return 10
    

def drawValues(canvas, cells, func, color):
    for cell in cells:
        pygame.draw.circle(
            canvas,
            color,
            [cell.x*GRIDSIZE, cell.y*GRIDSIZE],
            round(func(cell))
        )

def grayscale(num: float):
    return (255 * num, 255 * num, 255 * num)

def draw_map(map: WorldMap):
    """
    Because Pygame can only show one window at a time,
    the map can currently only be shown as a debug feature. 
    Later on, it would be nice to show a proper, larger map, maybe even as an html file.
    """
    width = map.width
    height = map.height

    size = [width*GRIDSIZE, height*GRIDSIZE]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Python MapGenerator")

    done = False
    clock = pygame.time.Clock()

    screen.fill(WHITE)
    drawCellColors2(screen, GRIDSIZE, map.cells)
    drawTrees(screen, map.cells)
    for road in map.roads:
        pygame.draw.lines(screen, ROAD, False, [(cell.x*GRIDSIZE, cell.y*GRIDSIZE) for cell in road])
    for road in map.sea_roads:
        pygame.draw.lines(screen, BLACK, False, [(cell.x*GRIDSIZE, cell.y*GRIDSIZE) for cell in road])
    for river in map.rivers:
        drawRiver(screen, river)
    
    #drawCities(screen, map.cells)
    #core = map.cities[0]
    #drawPoint(screen, (core.cell.x, core.cell.y), GRIDSIZE, RED)
    for city in map.cities:
        #print(city.wealth, city.pop_size, city.capacities.food_production, city.capacities.food_maximum, city.capacities.farming.worked)
        value = max(min(city.wealth * 0.01, 1), 0)
        #print(value)
        #value = 1 if city.title.de_facto_holder.is_female else 0
        drawPoint(screen, (city.cell.x, city.cell.y), GRIDSIZE, grayscale(value))
        """
        if core == city:
            continue
        if city.culture is not None:
            d = core.laws.culture_discrimination[city.culture].value
            drawPoint(screen, (city.cell.x, city.cell.y), GRIDSIZE, grayscale(d))
        else:
            print(city.id)
        """

    edge_counter = Counter()
    for route in map.traderoutes:
        for c1, c2 in zip(route[:-1], route[1:]):
            edge_counter[((c1.cell.x*GRIDSIZE, c1.cell.y*GRIDSIZE), (c2.cell.x*GRIDSIZE, c2.cell.y*GRIDSIZE))] += 1
    for edge, count in edge_counter.most_common():
        if count > 1:
            pygame.draw.line(screen, BLACK, edge[0], edge[1], round(count))

    #drawPath(screen, [p.cell for c in map.cities for p in c.ports], YELLOW)
    #drawPoint(screen, (map.cells[1048].x, map.cells[1048].y), GRIDSIZE, RED)

    for city in sorted(map.cities, key=lambda x: x.wealth):
        #print(city.capacities.trade.maximum, city.capacities.trade.worked, city.capacities.trade.production, city.wealth, city.pop_size)
        #if city.traderoute_counter > 0:
        print("="*80)
        print("Population:", city.pop_size)
        print("Wealth:", city.wealth)
        print("Traderoute Count:", city.traderoute_counter)
        print("Traderoute Value:", city.traderoute_wealth)
        print("Food Surplus:", city.capacities.food_production - city.pop_size)
        for cap in city.capacities.capacities:
            print("-"*80)
            print(cap.work_type)
            print("Workers:", cap.worked)
            print("Production:", cap.production)
        drawPoint(screen, (city.cell.x, city.cell.y), GRIDSIZE, RED, round(city.wealth * 0.005))
        drawPoint(screen, (city.cell.x, city.cell.y), GRIDSIZE, BLACK, round(city.capacities.artisan.production * 0.005))
       
    #pygame.draw.lines(screen, BLACK, False, [(r.cell.x*GRIDSIZE, r.cell.y*GRIDSIZE) for r in best_route[0]])
    #drawPoint(screen, (map.cities[595].cell.x, map.cities[595].cell.y), GRIDSIZE, GREEN)
    #drawPoint(screen, (map.cities[81].cell.x, map.cities[81].cell.y), GRIDSIZE, BLUE)
    #for n in map.cities[595].neighbors:
    #    drawPoint(screen, (n.cell.x, n.cell.y), GRIDSIZE, RED)
    #for n in map.cities[81].neighbors:
    #    drawPoint(screen, (n.cell.x, n.cell.y), GRIDSIZE, RED)
    #print(map.city_to_city_path(map.cities[595], map.cities[81]))
    #drawPath(screen, [c.cell for c in map.city_to_city_path(map.cities[24], map.cities[0])], RED)
    #drawPath(screen, map.cell_to_cell_path(map.cities[595].cell, map.cities[81].cell, test_pathfinding_cost), YELLOW)
    #drawPath(screen, [c for c in map.cells if c.is_border_cell_south], YELLOW)
    #drawValues(screen, map.cells, lambda x: x.fertility * 5, YELLOW)

    #drawPoints(screen, [(p.x, p.y) for p in map.cells if p.is_border_cell])
    """
    cell1 = cells[1056]
    cell2 = cells[8000]
    cell3 = cells[5000]
    print((cells[1056].x, cells[1056].y))
    print((cells[8000].x, cells[8000].y))
    print((cells[5000].x, cells[5000].y))
    print(cell1.get_direction(cell2))
    print(cell2.get_direction(cell1))
    print(cell2.get_direction(cell3))
    print(cell3.get_direction(cell1))
    drawPoint(screen, (cells[1056].x, cells[1056].y), GRIDSIZE, RED)
    drawPoint(screen, (cells[8000].x, cells[8000].y), GRIDSIZE, BLUE)
    drawPoint(screen, (cells[5000].x, cells[5000].y), GRIDSIZE, GREEN)
    """
    #drawPoints(screen, [(cell.x, cell.y) for cell in cells[1056].neighbors], GRIDSIZE)
    #drawCellColors(screen, GRIDSIZE, delaunay.triangles, len(delaunay.halfedges), centers, delaunay, elevation, moisture)
    pygame.display.flip()

    while not done:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done=True

        

    pygame.quit()


if __name__ == "__main__":
    import random
    random.seed(42)
    import pickle
    import sys
    sys.setrecursionlimit(9999999)
    map = pickle.load(open("mapfiles/test_routes.pkl", mode="rb"))
    draw_map(map)
