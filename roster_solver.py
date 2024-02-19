import random

from ortools.sat.cp_model_pb2 import CpSolverStatus
from ortools.sat.python import cp_model

# Sets the maximim number of solutions to find before stopping the search
SOLUTION_LIMIT = 100


class RosterProblem:
    def __init__(self, e: int, d: int, s: int, soft_days_off: bool) -> None:
        """
        Initializes the roster problem.

        Args:
            e (int): Number of employees.
            d (int): Number of days in the scheduling period.
            s (int): Number of shifts per day.
            soft_days_off (bool): Determines if the 'two days off' rule is a
            soft constraint (True) or hard constraint (False).
        """
        self.__e = e  # Number of employees
        self.__d = d  # Number of days
        self.__s = s  # Number of shifts
        self.__soft_days_off = soft_days_off
        self.__employees_range = range(1, self.__e + 1)
        self.__days_range = range(1, self.__d + 1)
        self.__shifts_range = range(1, self.__s + 1)
        self.__model = cp_model.CpModel()
        self.__solver = cp_model.CpSolver()
        self.__all_shifts = {}

    def create_variables(self) -> None:
        """
        Creates decision variables for the roster problem.

        Each variable represents a potential assignment of an employee to a
        shift on a given day. The method generates all combinations of
        mployees, days, and shifts and stores them as boolean variables in a
        dictionary.
        """
        all_shifts = {}
        for i in self.__employees_range:
            for j in self.__days_range:
                for k in self.__shifts_range:
                    all_shifts[(i, j, k)] = self.__model.NewBoolVar(
                        f"i={i}_j={j}_k={k}"
                    )
        self.__all_shifts = all_shifts

    def add_constraints(self) -> None:
        """
        Adds constraints to the roster problem model.

        The constraints include:
        1. Each employee works at most one shift per day.
        2. Each employee gets at most two days off (soft or hard constraint
        based on initialization).
        3. Each shift (except for the 'day off' shift) is covered by at least
        one employee.
        """
        # 1. Each employee works at most one shift per day
        for i in self.__employees_range:
            for j in self.__days_range:
                self.__model.AddExactlyOne(
                    self.__all_shifts[(i, j, k)] for k in self.__shifts_range
                )

        # Make 2 days off a soft constraint and then maximise
        if self.__soft_days_off:
            for i in self.__employees_range:
                self.__model.Add(
                    sum(self.__all_shifts[(i, j, 1)] for j in self.__days_range) <= 1
                )
            total_days_off = sum(
                self.__all_shifts[(i, j, 1)]
                for i in self.__employees_range
                for j in self.__days_range
            )
            self.__model.Maximize(total_days_off)
        else:
            # Make 2 days off a hard constraint
            for i in self.__employees_range:
                self.__model.Add(
                    sum(self.__all_shifts[(i, j, 1)] for j in self.__days_range) == 2
                )
        # 3. There must be an employee working on every shift
        # Explanation: For every shift, there has to be one employee assigned that is not on a day off
        for j in self.__days_range:
            for k in self.__shifts_range:
                if k != 1:  # Skip shift 1 which represents a day off
                    self.__model.Add(
                        sum(
                            self.__all_shifts[(i, j, k)] for i in self.__employees_range
                        )
                        > 0
                    )

        # assigmnments_matrix = [(2, 2), (2, 2), (1, 1), (2, 2), (1, 2), (2, 3)]
        # for j in self.__days_range:
        #    for k in self.__shifts_range:
        #        self.__model.Add(
        #            sum(self.__all_shifts[(i, j, k)] for i in self.__employees_range)
        #            >= assigmnments_matrix[j - 1][k - 2]
        #        )

        # workers_needed = sum(sum(pair) for pair in assigmnments_matrix)
        # workers_assigned = sum(
        #     self.__all_shifts[(i, j, k)]
        #     for i in self.__employees_range
        #     for j in self.__days_range
        #     for k in self.__shifts_range
        #     if k > 1
        # )
        # print(abs(workers_needed - workers_assigned))

    def print_stats(self, status: CpSolverStatus) -> None:
        """
        Prints solver statistics after solving the roster problem.

        Args:
            status (CpSolverStatus): The status of the solver after the search.
        """
        print("Statistics")
        print(f"  - status          : {self.__solver.StatusName(status)}")
        print(f"  - conflicts       : {self.__solver.NumConflicts()}")
        print(f"  - branches        : {self.__solver.NumBranches()}")
        print(f"  - wall time       : {self.__solver.WallTime()} s")

    def make_roster(self) -> dict:
        """
        Solves the roster problem and returns the first solution found.

        This method sets up the problem, solves it, and processes the solution
        into a readable format. It returns a dictionary containing the solution
        status, week length, and the roster data.

        Returns:
            dict: A dictionary with solution details, including the roster
            assignment for each employee.
        """
        self.create_variables()
        self.add_constraints()

        # Initialise return object
        data = {}

        # Initialise solution printer
        solution_printer = SolutionPrinter(
            self.__all_shifts, self.__e, self.__d, self.__s, SOLUTION_LIMIT
        )
        # Find all solutions (up to limit)
        self.__solver.parameters.enumerate_all_solutions = True
        status = self.__solver.Solve(self.__model, solution_printer)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # construct return object to return first solution
            data = {
                "status": 0,
                "num_solutions": len(solution_printer.solutions),
                "week_length": self.__d,
                "data": [],
            }
            print(len(solution_printer.solutions))
            solution = random.choice(solution_printer.solutions)
            # Filter assigned shifts
            assigned_shifts = [k for k, v in solution.items() if v == 1]
            for employee_num in self.__employees_range:
                shifts = [s for (e, _, s) in assigned_shifts if e == employee_num]
                data["data"].append(
                    {"employee_num": f"{employee_num}", "shifts": shifts}
                )
        else:
            # Failure
            data = {
                "status": 1,
                "num_solutions": 0,
                "week_length": -1,
                "data": [],
            }

        self.print_stats(status)
        return data


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, all_shifts, e, d, s, limit) -> None:
        """
        Initializes the solution printer callback.

        Args:
            all_shifts (dict): Dictionary of all shift variables.
            e (int): Number of employees.
            d (int): Number of days.
            s (int): Number of shifts.
            limit (int): The maximum number of solutions to print.
        """
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__all_shifts = all_shifts
        self.__e = e
        self.__d = d
        self.__s = s
        self.__limit = limit
        self.solutions = []

    def on_solution_callback(self) -> None:
        """
        Callback method called for each solution found by the solver.

        This method stores and prints each solution up to the specified limit.
        It then halts the search once the limit is reached.
        """
        solution = {}
        for i in range(1, self.__e + 1):
            for j in range(1, self.__d + 1):
                for k in range(1, self.__s + 1):
                    solution[(i, j, k)] = self.Value(self.__all_shifts[(i, j, k)])
        self.solutions.append(solution)
        self.print_solution(solution)
        if len(self.solutions) >= self.__limit:
            print(f"Stopped searching after {self.__limit} solutions.")
            self.StopSearch()

    def print_solution(self, solution: dict) -> None:
        """
        Prints a single solution in a readable format.

        Args:
            solution (dict): The solution to print, represented as a dictionary.
        """
        result = "\n"
        days = ["M", "T", "W", "T", "F", "S", "S"]
        header = ""
        for d in range(1, self.__d + 1):
            header += f"{days[d - 1]} "
        result += f"{header} \n"
        i = 1
        for shift in solution:
            if solution[shift] == 1:
                result += f"{shift[2]} "
                if i % self.__d == 0:
                    result += "\n"
                i += 1
        print(result)
