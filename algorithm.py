from ortools.sat.python import cp_model


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Stores solutions"""

    def __init__(self, roster, e, d, s, limit):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__roster = roster
        self.__e = e
        self.__d = d
        self.__s = s
        self.__limit = limit
        self.solutions = []

    def on_solution_callback(self):
        # Store all solutions in a list
        solution = {}
        for i in range(1, self.__e + 1):
            for j in range(1, self.__d + 1):
                for k in range(1, self.__s + 1):
                    solution[(i, j, k)] = self.Value(self.__roster[(i, j, k)])
        self.solutions.append(solution)
        if len(self.solutions) >= self.__limit:
            print(f"Stopped searching after {self.__limit} solutions.")
            self.StopSearch()


def main():
    # Initialise model
    model = cp_model.CpModel()

    # Define variables
    e = 1  # Number of employees
    d = 3  # Number of days in the work week
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
    for i in employees_range:
        for j in days_range:
            model.AddExactlyOne(roster[(i, j, k)] for k in shifts_range)

    # 2. TODO Each employee works at most 5 shift per week

    # 3. TODO Each shift must be covered by one employee

    # Solve
    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter(roster, e, d, s, 5)
    # Find solutions
    solver.parameters.enumerate_all_solutions = True
    status = solver.Solve(model, solution_printer)

    # Print solutions
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print()
        days = ["M", "T", "W", "T", "F", "S", "S"]
        for solution in solution_printer.solutions:
            header = ""
            for d in days_range:
                header += f"{days[d - 1]} "
            print(header)
            i = 1
            for shift in solution:
                if solution[shift] == 1:
                    print(f"{shift[2]} ", end="")
                    if i % d == 0:
                        print()
                    i += 1
            print()

    assert len(solution_printer.solutions) == 5

    # Print statistics
    print("Statistics")
    print("  - status          : %s" % solver.StatusName(status))
    print("  - conflicts       : %i" % solver.NumConflicts())
    print("  - branches        : %i" % solver.NumBranches())
    print("  - wall time       : %f s" % solver.WallTime())


if __name__ == "__main__":
    main()
