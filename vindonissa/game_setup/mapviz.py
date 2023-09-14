#!/usr/bin/env python3

import math
import pygame


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
        pygame.draw.polygon(screen, heightColorByCategory(cell), [(x * gridsize, y * gridsize) for x, y in cell.coords])


def drawPoints(screen, canvas, points, gridsize):
    for point in points:
        x = point[0]
        y = point[1]
        pygame.draw.circle(
            canvas,
            RED,
            [x*gridsize, y*gridsize],
            1
        )


def draw_map(width, height, delaunay, centers, elevation, moisture, points, cells):
    """
    Because Pygame can only show one window at a time,
    the map can currently only be shown as a debug feature. 
    Later on, it would be nice to show a proper, larger map, maybe even as an html file.
    """
    size = [width*GRIDSIZE, height*GRIDSIZE]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Python MapGenerator")

    done = False
    clock = pygame.time.Clock()

    screen.fill(WHITE)
    drawCellColors2(screen, GRIDSIZE, cells)
    #drawCellColors(screen, GRIDSIZE, delaunay.triangles, len(delaunay.halfedges), centers, delaunay, elevation, moisture)
    #drawPoints(screen, screen, points, GRIDSIZE)
    pygame.display.flip()

    while not done:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done=True

        

    pygame.quit()