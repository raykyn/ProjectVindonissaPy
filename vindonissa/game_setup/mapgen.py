#!/usr/bin/env python3

import math
from typing import List
from opensimplex import OpenSimplex
from random import random, randint

from vindonissa.game_objects.cell import Cell
from vindonissa.game_objects.map import WorldMap
from vindonissa.game_setup.Delaunator import Delaunator
from vindonissa.game_setup.mapviz import draw_map


def calculateCentroids(points, delaunay):
    numTriangles = len(delaunay.halfedges) / 3
    centroids = []
    for t in range(int(numTriangles)):
        sumOfX = 0
        sumOfY = 0
        for i in range(3):
            s = 3*t + i
            p = points[delaunay.triangles[s]]
            sumOfX += p[0]
            sumOfY += p[1]
        centroids.append({"x": sumOfX / 3, "y": sumOfY / 3})
    return centroids


def assignElevation(points, numRegions, width, height, wavelength):
    noise = OpenSimplex(seed=randint(0, 9999999))
    noise2 = OpenSimplex(seed=randint(0, 9999999))
    noise3 = OpenSimplex(seed=randint(0, 9999999))

    freq1 = 6
    freq2 = freq1 * 4
    freq3 = freq2 * 4

    elevation = []
    for r in range(numRegions):
        nx = points[r][0] / width - 0.5
        ny = points[r][1] / height - 0.5
        sample = ((1 * noise.noise2d(freq1 * nx / wavelength, freq1 * ny / wavelength) + 
                    0.5 * noise2.noise2d(freq2 * nx / wavelength, freq2 * ny / wavelength) +
                    0.25 * noise3.noise2d(freq3 * nx / wavelength, freq3 * ny / wavelength)) / 1.75)
        
        # shaping the landmass
        tx = max(0.3, points[r][0] / width)
        ty = max(0.3, points[r][1] / height)
        d = min(1, (tx * tx + ty * ty) / math.sqrt(2))
        sample = (1 + sample - d) / 2

        # valley factor
        sample = pow(sample * 1.6, 2.5).real

        # shaping the landmass (weaker shaping)
        tx = max(0.3, points[r][0] / width)
        ty = max(0.3, points[r][1] / height)
        d = min(1, (tx * tx + ty * ty) / math.sqrt(2))
        sample = (0.5 + sample - d*0.5) / 2
        
        elevation.append(sample)

    return elevation


def assignMoisture(points, numRegions, width, height, wavelength):
    noise = OpenSimplex(seed=randint(0, 99999))
    moisture = []
    for r in range(numRegions):
        nx = points[r][0] / width - 0.5
        ny = points[r][1] / height - 0.5
        moisture.append((1 + noise.noise2d(nx / wavelength, ny / wavelength)) / 2)
    return moisture


def get_elevation_thresholds(elevation: List[float]) -> float:
    """
    With this threshold we can for example make exactly a third of the map into water.
    currently returning: [waterlevel -> 0.3]
    """
    sorted_elevation = sorted(elevation)
    thresholds = [0.3, 0.5, 0.8, 0.95, 1]
    return [sorted_elevation[int(len(sorted_elevation) * t)-1] for t in thresholds]


def nextHalfedge(e):
    return e - 2 if e % 3 == 2 else e + 1


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


def create_cell_coordinates(numEdges, triangles, delaunay, centers):
    coords = {}

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
            coordinates = [[vertices[0]["x"], vertices[0]["y"]]]
            for i in range(1, len(vertices)):
                coordinates.append([vertices[i]["x"], vertices[i]["y"]])
            #pygame.draw.polygon(screen, biomeColor(r, elevation, moisture), coordinates)
            #pygame.draw.polygon(screen, heightColor(elevation[r]), coordinates)
            coords[r] = coordinates
    return coords


def create_worldmap(
        width: int = 120, 
        height: int = 80, 
        jitter: float = 0.5, 
        wavelength: float = 1, 
        wavelength_moisture: float = 1,
        draw_map_: bool = False) -> WorldMap:
    """
    Create a new map, including elevation, moisture, etc.
    """
    map: WorldMap = WorldMap(width, height)

    points = []
    for x in range(width):
        for y in range(height):
            points.append(
                [x + (jitter * (random() - random())),
                y + (jitter * (random() - random()))]
            )

    delaunay = Delaunator.Delaunator(points)
    centers = calculateCentroids(points, delaunay)
    elevation = assignElevation(points, len(points), width, height, wavelength)
    moisture = assignMoisture(points, len(points), width, height, wavelength_moisture)

    thresholds = get_elevation_thresholds(elevation)

    coords = create_cell_coordinates(len(delaunay.halfedges), delaunay.triangles, delaunay, centers)
    #print(len(coords), len(points), len(elevation))

    # Make each point a Cell object
    for (x, y), e, i in zip(points, elevation, range(len(points))):
        if i not in coords:
            continue
        for tr, t in enumerate(thresholds):
            if e <= t:
                break
        cell = Cell(x, y, e, e <= thresholds[0], coords[i], tr)
        map.cells.append(cell)

    if draw_map_:
        draw_map(width, height, delaunay, centers, elevation, moisture, points, map.cells)

if __name__ == "__main__":
    create_worldmap(draw_map_=True)
    