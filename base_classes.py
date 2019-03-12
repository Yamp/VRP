import scipy
from logging import root

from icecream import ic
from numba import jit

root.debug('Importing base_classes')

from dataclasses import dataclass, field
from typing import List, Set, Collection, Tuple
from geopy.distance import distance, vincenty

# TODO: OSRM + пометить машины, которые не могу проехать.
from geopandas.tests.test_geocode import geopy

from utils import static_field


@dataclass(frozen=True)
class Position:
    """Место в пространстве"""
    x: float = None
    y: float = None

    # @jit
    def dist(self, point: "Position") -> float:
        # return mpu.haversine_distance((self.x, self.y), (point.x, point.y))
        # return vincenty((self.x, self.y), (point.x, point.y)).km
        # return distance((self.x, self.y), (point.x, point.y)).km
        return (self.x - point.x) ** 2 + (self.y - point.y) ** 2


@dataclass(frozen=True)
class TimeConstraints:
    """Ограничения по времени"""
    open_time: float = float("-inf")
    close_time: float = float("+inf")

    def is_ok(self, t):
        return self.open_time <= t <= self.close_time


@dataclass(frozen=True)
class Geozone:
    """Геозона к которой принадлежит точка"""
    ABANDON_TYPES: tuple = static_field(val=('Никогда', 'Если нужно', 'Нежелательно'))
    ZONE_TRANSFER_COEFF: float = static_field(val=2)  # TODO: random magic number

    can_be_abandoned: str = 'Никогда'  # Можно ли машинкам выезжать из зоны?
    can_be_visited: str = 'Никогда'  # Можно ли другим заезжать в зону?


@dataclass(frozen=True)
class Place(Position):
    """ Любая штука, которая является местом на карте """
    zone: Geozone = Geozone()
    time_cons: TimeConstraints = TimeConstraints()


@dataclass(frozen=True)
class Base(Place):
    """ Гараж откуда машины выезжают и где хранятся контейнеры """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@dataclass(frozen=True)
class Unload(Place):
    """ Свалка куда машины вывозят мусор и полныен контейнеры """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@dataclass(frozen=True)
class VisitPoint(Place):
    """ Точка которую нужно обслужить """
    serving_time: float = 0  # Продолжительность обслуживания данной точки
    V: float = None  # Объем и вес груза
    m: float = None  # вес груза


@dataclass(frozen=True)
class NonRemovablePoint(VisitPoint):
    is_removable: bool = static_field(val=False)
    type: str = None  # тип груза


@dataclass(frozen=True)
class RemovablePoint(VisitPoint):
    TASKS: Tuple[str] = static_field(val=('Привезти емкость', 'Заменить на пустую',
                                  'Очистить с возвратом', 'Забрать полную'))
    is_removable: bool = static_field(val=False)
    task = str


class Road:
    def __init__(self):
        self.prohibited_car_types = set()


@dataclass(frozen=True)
class Vehicle:
    max_V: float = None
    max_m: float = None
    base: Base = Base()  # База на которую машина приезжает и уезжает
    vehicle_type: str = None  # Тип машины (по которому определяются доступность дорог)
    possible_storages: Set[Place] = frozenset()  # Перечень доступных складов
    allowed_point_types: Set[Place] = frozenset()  # Типы точек, которые может обслуживать данная машина
    work_time: TimeConstraints = TimeConstraints()  # рабочее время

    start_price: float = 0  # Затраты на выход в рейс
    km_price: float = 0  # Затраты на 1 километр пробега
    hour_price: float = 0  # Затраты на 1 час работы
    tonn_loading_price: float = 0  # Затраты на погрузку 1 тонны/куб.м грузов

    params = None  # Пользовательские параметры
    price_formula = None  # Пользовательская формула оценки затра

    # Машинка может забрать груз  TODO: что делать со временем
    def can_serve(self, p: VisitPoint) -> bool:
        constr = []
        constr += [p.m <= self.max_m]
        constr += [p.V <= self.max_V]
        constr += [p.type in self.allowed_point_types]

        return all(constr)

    def can_ride(self, r: Road) -> bool:
        return self.vehicle_type not in r.prohibited_car_types

    # def _default_calc_price(self, t: Tour) -> float:
    #     price = 0
    #     price += self.start_price
    #     price += self.km_price * t.get_length()
    #     price += self.hour_price * t.get_time()
    #     price += self.tonn_loading_price * t.get_charge_weight()
    #
    #     return price
    #
    # def calc_price(self, t: Tour) -> float:
    #     if self.price_formula is None:
    #         return self._default_calc_price(t)
    #     else:
    #         return self.price_formula(t)
    #
    # def tour_is_ok(self, t: Tour) -> bool:
    #     points_ok = all(self.can_serve(p) for p in t.get_visit_points())
    #     roads_ok = all(self.can_ride(r) for r in t.get_roads())
    #
    #     return points_ok and roads_ok


@dataclass
class Task:
    points: Collection[VisitPoint]
    bases: Set[Base]
    vehicles: Collection[Vehicle]
    unloads: Set[Unload]
