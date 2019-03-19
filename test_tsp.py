import tsplib95

from graph.graph import Graph
from tests.loaders.io_helper import read_tsp
from vendors.py_christofides import christofides

problem = tsplib95.load_problem('tests/data/uy734.tsp')
print(problem)

# problem = read_tsp('tests/data/uy734.tsp')
# print((problem.x, problem.y))
# gg = Graph.from_xy((problem.x, problem.y))
# matr = gg.matrix
# print(matr)
#
# TSP = christofides.compute(matr)
