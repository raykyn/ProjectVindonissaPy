#!/usr/bin/env python3

from collections import defaultdict
import math
from typing import List, Dict
from opensimplex import OpenSimplex
from random import random, randint, sample, choice

from vindonissa.game_objects.cell import Cell
from vindonissa.game_objects.map import WorldMap
from vindonissa.game_objects.river import River
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


def get_cell_neighbors(cells_by_id: Dict[int, Cell], numEdges, triangles, delaunay, centers):
    """
    A pretty clunky piece of code that looks up which cells share vertices so we know that
    they are neighbored. By no means perfect, but it does the job at least.
    """
    vertex_to_points = defaultdict(list)
    
    seen = set()
    for e in range(numEdges):
        r = triangles[nextHalfedge(e)]
        if r not in seen:
            seen.add(r)
            vertices = edgesArountPoint(delaunay, e)
            if len(vertices) < 3:
                continue
            vertices = [(centers[triangleOfEdge(x)]["x"], centers[triangleOfEdge(x)]["y"]) for x in vertices]
            # point_to_vertices[r] = set(vertices)
            for vertex in vertices:
                vertex_to_points[vertex].append(r)

    for vertex, points in vertex_to_points.items():
        current_cells: List[Cell] = []
        for point in points:
            cell = cells_by_id[point]
            cell.vertices.add(vertex)
            current_cells.append(cell)
        for i, a in enumerate(current_cells):
            for b in current_cells[i+1:]:
                if a in b.neighbors:
                    continue
                if len(a.vertices.intersection(b.vertices)) > 1:
                    a.neighbors.append(b)
                    b.neighbors.append(a)


def create_river(origin: Cell, 
                 upstream_tolerace: float = 0.1,
                 downstream_bonus_tr: float = 0.005) -> River:
    """
    I should probably replace this through an a* algorithm
    """

    river = River(origin)
    cell: Cell = origin
    last_direction: int = None
    continue_river = True
    while not cell.is_water and not cell.is_border_cell and continue_river:

        # choose neighbor to flow to
        neighbor_weights = []
        for neighbor in cell.neighbors:
            weight = 0
            if neighbor in river.path:
                neighbor_weights.append(0)
                continue
            elif neighbor.has_river:
                # allow merging if present river is not the same
                weight += 50
                

            """       
            if neighbor.elevation - upstream_tolerace > cell.elevation:
                continue
            elif neighbor.elevation < cell.elevation:
                bonus = round((cell.elevation - (neighbor.elevation)) / downstream_bonus_tr)
                weight += 1+bonus
            else:
                weight += 1
            """
            if cell.elevation_category > neighbor.elevation_category:
                weight += 100
            elif cell.elevation_category == neighbor.elevation_category:
                weight += 50
            else:
                weight += 1

            # bonus for going as straight as possible
            if last_direction is not None:
                new_direction = cell.get_direction(neighbor)
                angle = abs(last_direction - new_direction)

                weight += 0
                #weight += round((180 - angle) / 180)

            neighbor_weights.append(weight)
            
        try:
            next_cell = sample(cell.neighbors, 1, counts=neighbor_weights)[0]
        except ValueError as e:
            return None
            #return river if len(river.path) > 1 else None

        if next_cell.has_river:
            # if we merged rivers, we need to stop generation here
            continue_river = False

        river.path.append(next_cell)
        cell = next_cell
        last_direction = next_cell.get_direction(cell)
        #last_direction = cell.get_direction(next_cell)

    # only make river connects if river is actually made
    for cellA, cellB in zip(river.path[:-1], river.path[1:]):
        cellA.river_connections.append((river, cellB, "out"))
        cellB.river_connections.append((river, cellA, "in"))

    return river



def create_rivers(map: WorldMap, river_perc: int) -> List[River]:
    river_weights: List[int] = []
    for cell in map.cells:
        if cell.is_water or cell.is_border_cell:
            river_weights.append(0)
        elif cell.elevation_category == 1:
            river_weights.append(1)
        elif cell.elevation_category == 2:
            river_weights.append(2)
        elif cell.elevation_category == 3:
            river_weights.append(8)
        elif cell.elevation_category == 4:
            river_weights.append(4)

    river_budget = round(len(map.land_cells) * river_perc)

    origins: List[Cell] = sample(map.cells, river_budget, counts=river_weights)

    rivers = []

    for origin in origins:
        if origin.has_river:
            continue
        if river_budget <= 0:
            break
        new_river: River = create_river(origin)
        if new_river is None:
            # river couldn't be created
            continue
        river_budget -= len(new_river)
        rivers.append(new_river)

    return rivers


def create_worldmap(
        width: int = 120, 
        height: int = 80, 
        jitter: float = 0.5, 
        wavelength: float = 1, 
        wavelength_moisture: float = 1,
        draw_map_: bool = False,
        river_perc: int = 0.2) -> WorldMap:
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
        cell = Cell(i, x, y, e, e <= thresholds[0], coords[i], tr)
        map.cells.append(cell)

    # assign neighbors
    map.setup_cells()
    get_cell_neighbors(map.cells_by_id, len(delaunay.halfedges), delaunay.triangles, delaunay, centers)

    # create rivers
    map.rivers = create_rivers(map, river_perc)

    if draw_map_:
        draw_map(width, height, delaunay, centers, elevation, moisture, points, map)

    return map

if __name__ == "__main__":
    create_worldmap(draw_map_=True)
    