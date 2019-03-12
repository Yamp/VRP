import os
import pickle
from pathlib import Path
from typing import Tuple

import pandas as pd
from dateutil.parser import parse

from base_classes import *


# парсит время в формате HH:mm, возвращает число секунд с начала дня
from utils import logged, root_logger, pickle_cached


def parse_time(s):
    return s


# парсит координаты x, y
def parse_coords(s):
    x, y = map(float, s.split(','))
    return x, y


# парсит все типы перевозимых грузов через пробелы, возвращает коллекцию
def parse_types(s):
    return set(s.split(' '))


@pickle_cached
def parse_data() -> Tuple:
    apps = pd.read_excel('data/applications.xlsx', header=1, usecols=range(1, 19))
    df = apps.copy()
    df.dropna(axis=1, how='all', inplace=True)  # дропаем пустые столбцы
    df.dropna(axis=0, how='all', inplace=True)  # дропаем пустые колонки
    df.columns = list(range(len(df.columns)))
    df.drop([0, 1, 9], axis=1, inplace=True)
    df.columns = ['xy', 'm', 'V', 'from_t', 'to_t', 'load_t', 'types', 'unload']
    apps = df

    cars = pd.read_excel('data/vehicles.xlsx', header=1, usecols=range(1, 10))
    df = cars.copy()
    df.dropna(axis=1, how='all', inplace=True)  # дропаем пустые столбцы
    df.dropna(axis=0, how='all', inplace=True)  # дропаем пустые колонки
    df.columns = list(range(len(df.columns)))
    df.drop([0, 1, 6], axis=1, inplace=True)
    df.columns = ['max_m', 'max_V', 'from_t', 'to_t', 'base_xy', 'types']
    cars = df

    return apps, cars


@pickle_cached
def fill_models(apps: pd.DataFrame, cars: pd.DataFrame) -> Task:
    points = []  # точки для работы
    unloads = set()  # точки куда мы будем все скидывать
    vehicles = []  # все машинки с их инфой
    bases = set()

    for i, app in apps.iterrows():  # распарсмим все в таблице заявок
        x, y = map(float, app.xy.split(','))
        V = float(app.V)
        m = float(app.m)
        time_cons = TimeConstraints(parse_time(app.from_t), parse_time(app.to_t))
        serving_time = app.load_t
        type = app.types

        p = NonRemovablePoint(x=x, y=y, V=V, m=m,
                       time_cons=time_cons, serving_time=serving_time, type=type)

        unloads.add(Unload(*parse_coords(app.unload)))
        points.append(p)

    for i, car in cars.iterrows():  # распарсим все в таблице приложений
        max_V = float(car.max_V)  # max_m
        max_m = float(car.max_m)  # max_V
        tc = TimeConstraints(parse_time(car.from_t), parse_time(car.to_t))  # time constr
        types = parse_types(car.types)  # types (все допустимые типы контейнеров)

        base = Base(*parse_coords(car.base_xy))  # base_xy
        v = Vehicle(max_V=max_V, max_m=max_m, work_time=tc, base=base, allowed_point_types=types)

        vehicles.append(v)
        bases.add(base)

    return Task(points, bases, vehicles, unloads=unloads)


apps, cars = parse_data()
task = fill_models(apps, cars)


