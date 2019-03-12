#!/usr/bin/env python

"""
This Python code is based on Java code by Lee Jacobson found in an article
entitled "Applying a genetic algorithm to the travelling salesman problem"
that can be found at: http://goo.gl/cJEY1
"""
import logging
import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from itertools import chain
from logging import root

from concorde.tsp import TSPSolver

from base_classes import VisitPoint
from genetics.genetic_utils import random_pair, randbool, randint, ArrayMutator
from map_model import Tour, Navigator, MapModel, SimpleMapModel


class BaseGeneticSample:
    @abstractmethod
    def crossover(self, other: "BaseGeneticSample") -> "BaseGeneticSample":
        pass

    @abstractmethod
    def mutate(self) -> "BaseGeneticSample":
        pass

    @abstractmethod
    def fitness(self) -> float:
        pass


class GeneticSolver:
    def __init__(self, gene_type, N=100, mutation_rate=0.05, elitism_ratio=0.5):
        self.N = N
        self.mutation_rate = mutation_rate
        self.elitism_ratio = elitism_ratio
        root.debug('Creating population')
        self.population = []
        for i in range(self.N):
            root.debug(f"Creating {i}th individual")
            self.population += [gene_type()]


    @staticmethod
    def _get_el_fitness(x):
        return x.fitness()

    def init_population(self):
        for i in range(self.N):
            self.population += OptimizableTour()

    def evolve(self):
        self.population.sort(key=self._get_el_fitness, reverse=True)
        first_dead = int(self.N * self.elitism_ratio)
        for i in range(first_dead, self.N):
            root.debug(f'Crossover {i}')

            i1 = randint(0, first_dead - 1)
            i2 = randint(0, first_dead - 1)

            newborn = self.population[i1].crossover(self.population[i2])
            if random.random() < self.mutation_rate:
                newborn.mutate()

            self.population[i] = newborn

    def get_fittest(self):
        return max(self.population, key=self._get_el_fitness)

    # def tournamentSelection(self, pop):
    #     tournament = Population(self.tourmanager, self.tournamentSize, False)
    #     for i in range(0, self.tournamentSize):
    #         randomId = int(random.random() * pop.populationSize())
    #         tournament.saveTour(i, pop.getTour(randomId))
    #     fittest = tournament.getFittest()
    #     return fittest


class OptimizableTour(BaseGeneticSample, Tour):
    mutator = ArrayMutator()
    navigator = Navigator(SimpleMapModel())

    def __init__(self, *args, **kwargs):
        if not args and not kwargs:
            self.places = self.navigator.map.all_places
            self.start_time = 0
            self.randomize()
        else:
            Tour.__init__(self, *args, **kwargs)
        self._fitness = self.calc_fitness()

    def crossover(self, other: "OptimizableTour") -> "OptimizableTour":
        child = self.mutator.crossover(self.places, other.places)
        return OptimizableTour(child, self.start_time)

    def mutate(self) -> "BaseGeneticSample":
        self.mutator.mutate(self.places)

    def calc_fitness(self):
        return -self.navigator.get_length(self)
        # return self.navigator.get_time(self) + self.navigator.get_length(self)

    def fitness(self) -> float:
        return self._fitness


def test_module():
    gs = GeneticSolver(gene_type=OptimizableTour, N=200, mutation_rate=0.2)

    places = gs.population[0].places
    xs = [p.x for p in places]
    ys = [p.x for p in places]

    print(xs)
    print(ys)
    solver = TSPSolver.from_data(xs=xs, ys=ys, norm="EUC_2D")
    solution = solver.solve()
    print(solution.optimal_value)
    print(solution.tour)

    for i in range(1000):
        gs.evolve()
        ff = [f.fitness() for f in gs.population]
        print(ff)

root.setLevel(logging.INFO)
test_module()
