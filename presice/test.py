from concorde.tsp import TSPSolver

solver = TSPSolver.from_data(xs=(18, 6, 2, 2, 5), ys=(7, 12, 3, 6, 8), norm="EUC_2D")
solution = solver.solve()
print(solution.optimal_value)
print(solution.tour)

