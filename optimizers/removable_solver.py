from collections import defaultdict
from itertools import product

from numpy import path
from scipy.optimize import linear_sum_assignment
import numpy as np

from base_classes import *
from map_model import SimpleMapModel


#  algorithm for finding best pairs
def hungrian_algorithm(p1: List[Place], p4: List[Place]):
    matr = np.fromfunction(lambda i, j: p1[i].dist(p4[j]), (len(p1), len(p4)), dtype=float)
    row_ind, col_ind = linear_sum_assignment(matr)

    res = []
    for i, j in zip(row_ind, col_ind):
        res.append((p1[i], p4[j]))

    return res


class RemovableOptimizer:
    def __init__(self, task: Task, map: SimpleMapModel):
        self.map = map
        self.vehicles = task.vehicles

        self.removables = [t for t in task.points if isinstance(t, RemovablePoint)]

        self.p1 = [t for t in self.removables if t.task == 'Привезти емкость']
        self.p2 = [t for t in self.removables if t.task == 'Заменить на пустую']
        self.p3 = [t for t in self.removables if t.task == 'Очистить с возвратом']
        self.p4 = [t for t in self.removables if t.task == 'Забрать полную']

        self.unloads = task.unloads
        self.bases = task.bases

        self.res_independent_chunks = []

    def get_best_1_4_pairs(self):
        pairs = hungrian_algorithm(self.p1, self.p4)
        paths = []

        for p in pairs:
            unload_pairs = product(self.unloads, self.unloads)
            us = min(unload_pairs, key=lambda x: p[0].dist(x[0]) + p[1].dist(x[1]))
            paths += [(us[0], p[0], p[1], us[1])]

        left_1 = set(self.p1) - set([p[0] for p in pairs]) if len(paths) < len(self.p1) else []
        left_4 = set(self.p4) - set([p[1] for p in pairs]) if len(paths) < len(self.p4) else []

        return paths, left_1, left_4

    def get_2_type_paths(self):
        paths = []
        groups = defaultdict(list)

        for p in self.p2:
            u = min(self.unloads, key=p.dist)
            groups[u] += p
            paths += [(u, p, u)]

    def get_3_paths(self):
