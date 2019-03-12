from logging import root

from utils import pickle_cached

root.debug('Importing map_model')
from dataclasses import dataclass
import random
from typing import List

from scipy.interpolate import interp1d, splrep
from scipy import interpolate

from base_classes import Place
from data_loaders import task
from abc import ABC, abstractmethod

root.debug('Importing map_model classes')


class MapModel(ABC):
    @abstractmethod
    def get_speed(self, p1, p2, start_time):
        pass

    @abstractmethod
    def get_dist(self, p1, p2, start_time):
        pass

    def get_time(self, p1: Place, p2: Place, start_time):
        return self.get_dist(p1, p2, start_time) / self.get_speed(p1, p2, start_time)


class SimpleMapModel(MapModel):
    # https://yandex.ru/company/researches/2017/moscow_traffic_2017
    # тестовые скорости движения от времени
    hour_speed = {
        0: 95, 1: 100, 2: 100, 3: 100, 4: 100, 5: 90, 6: 80, 7: 60, 8: 35, 9: 35, 10: 40, 11: 40,
        12: 40,
        13: 40, 14: 40, 15: 40, 16: 40, 17: 32, 18: 30, 19: 35, 20: 45, 21: 60, 22: 80, 23: 90,
        24: 95}
    # и фиганем сплайн от всего этого
    tck = interpolate.splrep(list(hour_speed.keys()), list(hour_speed.values()), s=0)

    __instance = None

    def __new__(cls):
        if SimpleMapModel.__instance is None:
            SimpleMapModel.__instance = object.__new__(cls)
        return SimpleMapModel.__instance

    def __init__(self):
        self.task = task
        self.points = task.points
        self.vehicles = task.vehicles
        self.unloads = task.unloads
        self.bases = task.bases

        self.all_places = (self.points + list(self.unloads) + list(self.bases))[:100]
        self.weights = {p:random.random() for p in self.all_places}

    def __get_avg_speed(self, time):
        return interpolate.splev(time / 3600, self.tck, der=0)

    def get_speed(self, p1, p2, start_time):
        return 100 * self.weights[p1] * self.weights[p2] + self.__get_avg_speed(start_time) * (
                    1 - self.weights[p1] * self.weights[p2])

    def get_dist(self, p1: Place, p2: Place, start_time):
        return p1.dist(p2)


@dataclass
class Tour:
    places: List[Place]
    start_time: float

    @property
    def N(self):
        return len(self.places)

    def randomize(self):
        random.shuffle(self.places)

    def __iter__(self):
        return iter(self.places)

    def __next__(self):
        return next(self.places)

    def __len__(self):
        return len(self.places)


class Navigator:
    def __init__(self, map_model: MapModel):
        self.map = map_model

    def get_length(self, tour: Tour) -> float:
        res = 0
        time = tour.start_time

        for i in range(len(tour.places) - 1):
            res += self.map.get_dist(tour.places[i], tour.places[i+1], time)
            time += self.map.get_time(tour.places[i], tour.places[i+1], time)

        return res

    def get_time(self, tour):
        res = 0
        time = tour.start_time

        for i in range(len(tour.places) - 1):
            res += self.map.get_time(tour.places[i], tour.places[i + 1], time)
            time += self.map.get_time(tour.places[i], tour.places[i + 1], time)

        return res

    def avg_speed(self, tour):
        return self.get_length(tour) / self.get_time(tour)

root.debug('Imported map_model classes')
