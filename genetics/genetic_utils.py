import random
import fastrand
from functools import reduce
from itertools import chain
from typing import List, Tuple
from collections import deque

from _pytest import unittest
from icecream import ic


def randint(a, b):
    return fastrand.pcg32bounded(b - a + 1) + a


def random_pair(n):
    a, b = randint(0, n - 1), randint(0, n - 1)
    return min(a, b), max(a, b)


def randbool():
    return random.random() > 0.5


def rand_reversed(l):
    if randbool():
        l = reversed(l)
    return l


def check_ok(l: List):
    assert None not in l
    assert len(set(l)) == len(l)


class ArrayMutator:
    def _rnd_i(self, l: List) -> int:
        """ Сгенерить рандомных индекс """
        return randint(0, len(l) - 1)

    def _2_sort_i(self, l: List) -> Tuple[int, int]:
        """ Сгенерировать 2 отсортированных индекса """
        a, b = self._rnd_i(l), self._rnd_i(l)
        return min(a, b), max(a, b)

    def _get_rnd_sorted_i(self, n: int, max_i: int) -> List[int]:
        """ Сгенегировать n отсортированных индексов """
        inds = [randint(0, max_i - 1) for i in range(n)]
        return sorted(inds)

    def reverse_chunk(self, l: List):
        """ Перевернуть кусок пути """
        a, b = self._rnd_i(l), self._rnd_i(l)
        a, b = min(a, b), max(a, b)
        l[a:b + 1] = reversed(l[a:b + 1])

    def change_2(self, l: List):
        """ Поменять 2 точки местами """
        a, b = self._2_sort_i(l)
        l[a], l[b] = l[b], l[a]

    def shift_chunk(self, l: List):
        """ Переместить точку вперед """
        a, b = self._2_sort_i(l)
        n = self._rnd_i(range(b - a + 1))
        d = deque(l[a:b])
        d.rotate(n)
        l[a:b] = rand_reversed(d)

    def change_groups(self, l: List):
        """ Поменять местами 2 группы точек """
        a, b, c, d = self._get_rnd_sorted_i(4, len(l) - 1)
        res = chain(l[0:a], rand_reversed(l[c + 1:d + 2]), l[b + 1:c + 1],
                    rand_reversed(l[a:b + 1]), l[d + 2:])
        l.clear()
        l.extend(res)

    def recombine(self, l: List):
        """ Меняем местами и переворачиваем произвольное количество кусков """
        ch_n = randint(1, 2)
        seps = self._get_rnd_sorted_i(ch_n, len(l) - 1)

        chunks = []
        for a, b in zip([0] + seps, seps + [len(l)]):
            ch = l[a:b]
            if randbool():
                ch = reversed(ch)
            chunks.append(ch)
        random.shuffle(chunks)

        res = chain(*chunks)

        l.clear()
        l.extend(res)

    def change_equal_groups(self, l):
        """ Меняем местами 2 группы точек равного размера (это мб быстрее) """
        unused_space = len(l)
        ch_len = (self._rnd_i(l) - 1) // 2
        unused_space -= 2 * ch_len

        st = randint(0, unused_space)
        unused_space -= st

        mid = randint(0, unused_space)

        a, b = st, st + ch_len
        c, d = b + mid, b + mid + ch_len

        for i in range(ch_len):
            l[a + i], l[c + i] = l[c + i], l[a + i]

    def shift_all(self, l):
        """ Меняем местами 2 группы точек равного размера (это мб быстрее) """
        n = self._rnd_i(l)
        d = deque(l)
        d.rotate(n)
        d = list(d)
        res = chain(rand_reversed(d[:n]), rand_reversed(d[n:]))

        l.clear()
        l.extend(res)

    def mutate(self, l):
        methods = [self.reverse_chunk, self.change_2, self.shift_chunk, self.shift_all,
                   self.change_groups, self.change_equal_groups, self.recombine]
        random.choice(methods)(l)

    def crossover(self, l1, l2):
        start, end = random_pair(len(l1))  # первый и последний элемент p1
        child = [None] * len(l1)  # будущий ребенок
        parents = [l1, l2]
        random.shuffle([l1, l2])  # перемешанные родители
        p1, p2 = parents

        from_p1 = set(p1[start:end + 1])  # словарь того, что будем повторять
        child[start:end + 1] = p1[start:end + 1]  # копируем кусок в ребенка
        child_slots = chain(range(0, start), range(end + 1, len(p1)))  # сохраняем пустые места

        for pl in p2:
            if pl not in from_p1:
                child[next(child_slots)] = pl

        return child


def test_module():
    asdf = ArrayMutator()

    N = 40
    for i in range(20000):
        print(f'test {i}')
        l1, l2 = list(range(N)), list(range(N))
        asdf.mutate(l1)
        ch = asdf.crossover(l1, l2)

        assert len(l1) == N
        check_ok(l1)

        assert len(ch) == N
        check_ok(ch)
