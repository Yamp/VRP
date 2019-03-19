import math

import numpy as np
from numba import jit

from base_classes import Position
from map_model import Tour


class Graph:
    @staticmethod
    def from_tour(points: Tour):
        res = Graph(len(points))

        for i1, p1 in enumerate(points):
            for i2, p2 in enumerate(points):
                res.matrix[i1][i2] = p1.dist(p2)

        return res

    @staticmethod
    def from_coords(coords):
        res = Graph(len(coords))

        for i1, p1 in enumerate(coords):
            for i2, p2 in enumerate(coords):
                res.matrix[i1][i2] = math.sqrt((p1 - x2) ** 2 + (y1 - y2) ** 2)

        return res

    @staticmethod
    def from_xy(xy):
        coords = tuple(zip(*xy))
        return Graph.from_coords(coords)

    def __init__(self, n):
        self.matrix = np.zeros((n, n))
