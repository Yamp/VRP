from collections import defaultdict
import heapq


class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance

    def dijsktra(self, start, end):
        heap = [(0, start)]  # cost from start node, end node
        visited = []
        while heap:
            (cost, u) = heapq.heappop(heap)
            if u in visited:
                continue
            visited.append(u)
            if u == end:
                return cost
            for v, c in self[u]:
                if v in visited:
                    continue
                next = cost + c
                heapq.heappush(heap, (next, v))
        return (-1, -1)

    def bellman_ford(self, initial):
        nl = len(self.nodes) + 1
        A = {v: [float("+inf")] * nl for v in self.nodes}
        P = {v: [None] * nl for v in self.nodes}
        A[initial][0] = 0

        for i in range(1, nl):
            found_better = 0
            for e, d in self.distances.items():
                u, v = e
                found_better = A[v][i] > A[v][i - 1] + d
                if A[v][i] > A[v][i-1] + d:
                    A[v][i] = A[v][i-1] + d
                    P[v][i] = u

        path = []
        j = nl
        while j > 0:
            path[j] = i
            i = P[i][j]
            j -= 1

        return path


gg = Graph()
[gg.add_node(a) for a in (1, 2, 3, 4, 5)]
gg.add_edge(1, 2, 5)
gg.add_edge(1, 3, 8)
# gg.add_edge(1, 4, -5)
gg.add_edge(1, 4, 5)
gg.add_edge(2, 3, 1)
gg.add_edge(5, 3, 2)
# gg.add_edge(5, 3, -2)
gg.add_edge(3, 3, 12)

p = gg.dijsktra(1)

print(p)

