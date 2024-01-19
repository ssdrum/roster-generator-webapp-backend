from ortools.sat.python import cp_model


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Stores intermediate solutions"""

    def __init__(self, roster, e, d, s):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.roster = roster
        self.e = e
        self.d = d
        self.s = s
        self.solutions = []

    def on_solution_callback(self):
        # Store all solutions in a list
        solution = {}
        for i in range(1, self.e + 1):
            for j in range(1, self.d + 1):
                for k in range(1, self.s + 1):
                    solution[(i, j, k)] = self.Value(self.roster[(i, j, k)])
        self.solutions.append(solution)


def main():
    # Initialise model
    model = cp_model.CpModel()

    # Define variables
    e = 3  # Number of employees
    d = 7  # Number of days in the workw eek
    s = 3  # Number of shifts

    employees_range = range(1, e + 1)
    days_range = range(1, d + 1)
    shifts_range = range(1, s + 1)

    # Define X
    roster = {}
    for i in employees_range:
        for j in days_range:
            for k in shifts_range:
                roster[(i, j, k)] = model.NewBoolVar(f"i={i}_j={j}_k={k}")

    # Constraints
    # 1. Each employee works at most one shift per day

    # Solve
    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter(roster, e, d, s)
    # Find all solutions
    solver.SearchForAllSolutions(model, solution_printer)


if __name__ == "__main__":
    main()
