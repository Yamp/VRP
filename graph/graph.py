import numpy as np
from numba import jit

from base_classes import Position
from map_model import Tour


class Graph:
    @jit
    @staticmethod
    def from_tour(points: Tour):
        res = Graph(len(points))

        for i1, p1 in enumerate(points):
            for i2, p2 in enumerate(points):
                res.matrix[i1][i2] = p1.dist(p2)

    def from_coords(self, coords=List[int, int]):
        return

    def __init__(self, n):
        self.matrix = np.zeros((n, n))
