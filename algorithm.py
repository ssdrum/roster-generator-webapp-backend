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


def generate_roster(e: int, d: int, s: int):
    """
    e: Number of employees.
    d: Number of days in the working week
    s: Number of shifts
    """

    try:
        assert e > 0 and d > 0 and s > 0
    except AssertionError:
        return "Invalid parameters"

    model = cp_model.CpModel()

    # Define variables
    employees_range = range(1, e + 1)
    days_range = range(1, d + 1)
    shifts_range = range(1, s + 1)  # shift 1 == day off

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

    # 2. Each employee gets 2 days off per week
    for i in employees_range:
        for j in range(1, d + 1):
            model.Add(sum(roster[(i, j, 1)] for j in days_range) == 2)

    # 3. There must be an employee working on every shift
    # Explanation: For every shift, there has to be one employee assigned that is not on a day off
    for j in days_range:
        for k in shifts_range:
            if k != 1:  # Skip shift 1 which represents a day off
                model.Add(sum(roster[(i, j, k)] for i in employees_range) > 0)

    # Solve
    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter(roster, e, d, s, 5)
    # Find solutions
    solver.parameters.enumerate_all_solutions = True
    status = solver.Solve(model, solution_printer)

    # Print solutions
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        result = ""
        result += "\n"
        days = ["M", "T", "W", "T", "F", "S", "S"]
        for solution in solution_printer.solutions:
            header = ""
            for d in days_range:
                header += f"{days[d - 1]} "
            result += f"{header} \n"
            i = 1
            for shift in solution:
                if solution[shift] == 1:
                    result += f"{shift[2]} "
                    if i % d == 0:
                        result += "\n"
                    i += 1
            result += "\n"

    assert len(solution_printer.solutions) == 5

    # Print statistics
    print("Statistics")
    print("  - status          : %s" % solver.StatusName(status))
    print("  - conflicts       : %i" % solver.NumConflicts())
    print("  - branches        : %i" % solver.NumBranches())
    print("  - wall time       : %f s" % solver.WallTime())

    return result


if __name__ == "__main__":
    main()
