"""
Sudoku class and solver for the
Insight Data Engineering coding challenge
written by Jim Bridgewater for Python 2.7.8
"""

# import required libraries
import csv
import numpy
import random


################################################################################
# Class definition
################################################################################

class Sudoku(object):
    """ Sudoku class for the Insight Data Engineering coding challenge """

    def __init__(self):

        # puzzle values
        self._puzzle = numpy.zeros([9, 9], numpy.int)

        # solution values
        self._solution = numpy.zeros([9, 9], numpy.int)

        # the values that can be entered in each location
        # without duplicating any of the numbers in the
        # row, column, or region that contain that location
        self._possible_values = list(
            [[[i + 1 for i in range(9)] for j in range(9)] for k in range(9)])

        # the number of values that can be entered in each location
        # without duplicating any of the numbers in the
        # row, column, or region that contain that location
        self._possibilities = 9*numpy.ones([9, 9], numpy.int)


    def puzzle_from_csv(self, file_name):
        """ Read in a Sudoku puzzle from a file of comma separated values """

        error_message = file_name + \
        "does not appear to be a valid 9 by 9 Sudoku puzzle."
        try:
            file_handle = open(file_name)
            csvreader = csv.reader(file_handle, skipinitialspace=True)
            data_list = []
            for line in csvreader:
                row = list(int(i) for i in line)
                if len(row) == 9:
                    data_list.append(row)
                else:
                    exit(error_message)
        except:
            exit(error_message)
        if len(data_list) != 9:
            exit(error_message)
        self._puzzle = numpy.array(data_list)
        self._solution = numpy.array(data_list)
        self._update_possible_values()


    def _update_possible_values(self):
        """
        Updates _possible_values and _possibilities
        after changes to _solution.
        """
        for i in range(9):
            for j in range(9):
                possible_values = self._find_possible_values(i, j)
                self._possible_values[i][j] = possible_values
                self._possibilities[i][j] = len(possible_values)


    def _find_possible_values(self, row, column):
        """
        Returns a list of the possible values a grid location can take without
        duplicating any of the values in its row, column, or 3 by 3 region.
        """
        if self._solution[row, column] in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            possible_values = [self._solution[row, column]]
        else:
            possible_values = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            affected_locations = _affected_locations(row, column)
            for i in range(9):
                for j in range(9):
                    if affected_locations[i, j] == 1:
                        # remove values found in the row, column and region
                        value = self._solution[i, j]
                        if value in possible_values:
                            possible_values.remove(value)
        return possible_values


    def add_value_to_puzzle(self, value, row, column):
        """
        Add a value to one location in the Sudoku puzzle and update
        the solution, possible_values and possibilities properties.
        """
        if value != 0:
            # update puzzle
            self._puzzle[row, column] = value
            # update solution
            self._solution[row, column] = value
            # update possible_values and possibilities
            affected_locations = _affected_locations(row, column)
            for i in range(9):
                for j in range(9):
                    if affected_locations[i, j] == 1:
                        if value in self._possible_values[i][j]:
                            self._possible_values[i][j].remove(value)
                            possibilities = len(self._possible_values[i][j])
                            self._possibilities[i][j] = possibilities


    def print_puzzle(self):
        """ Print a 9 by 9 Sudoku puzzle """
        error_message = "Data for method print_puzzle " + \
        "does not appear to be a valid 9 by 9 Sudoku puzzle."
        _print_grid(self._puzzle, error_message)


    def print_solution(self):
        """ Print the solution to a 9 by 9 Sudoku puzzle """
        error_message = "Data for method print_solution " + \
        "does not appear to be a valid solution to a 9 by 9 Sudoku puzzle."
        _print_grid(self._solution, error_message)


    def write_puzzle_to_csv(self, file_name):
        """
        Write a Sudoku puzzle to a file of comma separated values
        """
        error_message = "Data for " + file_name + \
        "does not appear to be a valid 9 by 9 Sudoku puzzle."
        _grid_to_csv(self._puzzle, file_name, error_message)


    def write_solution_to_csv(self, file_name):
        """
        Write the solution of a Sudoku puzzle
        to a file of comma separated values
        """
        error_message = "Data for " + file_name + \
        "does not appear to be a valid 9 by 9 Sudoku solution."
        _grid_to_csv(self._solution, file_name, error_message)


    def _valid_solution(self):
        """ Test the validity of a proposed Sudoku solution """

        valid = True
        # check rows
        for row in self._solution:
            for entry in row:
                # all entries must be 1-9
                if entry not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    valid = False
                # all entries in a row must be unique
                if sum(list(int(i == entry) for i in row)) > 1:
                    valid = False

        # check columns
        for column in numpy.transpose(self._solution):
            for entry in column:
                # all entries must be 1-9
                if entry not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    valid = False
                # all entries in a column must be unique
                if sum(list(int(i == entry) for i in column)) > 1:
                    valid = False

        # check 3 by 3 regions
        regions = list(
            self._solution[i:i+3, j:j+3] for i in [0, 3, 6] for j in [0, 3, 6])
        for region in regions:
            region_entries = region.reshape(1, 9)[0]
            for entry in region_entries:
                # all entries must be 1-9
                if entry not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    valid = False
                # all entries in a region must be unique
                if sum(list(int(i == entry) for i in region_entries)) > 1:
                    valid = False

        return valid


    def solve(self):
        """
        Solve the Sudoku puzzle. Start by searching for empty locations that
        have only one possible value. If any are found, enter the only possible
        value in those locations, update possible_values and try again. Stop
        when no more are found.
        """
        try_again = True
        while try_again:
            try_again = False
            for i in range(9):
                for j in range(9):
                    if self._solution[i][j] == 0:
                        if self._possibilities[i][j] == 1:
                            try_again = True
                            only_possible_value = self._possible_values[i][j][0]
                            self._solution[i][j] = only_possible_value
            self._update_possible_values()


    def initialize_randomly(self):
        """ Generate a Sudoku puzzle """

        for row in range(9):
            for column in range(9):
                self._puzzle[row, column] = random.choice(
                    _possible_values(self._puzzle, row, column))
                self.print_puzzle()


################################################################################
# Function definitions
################################################################################

def _grid_to_csv_string(grid_data, error_message):
    """
    Make a string of comma separated values from a 9 by 9 grid of numbers
    """
    if grid_data.size != 81:
        exit(error_message)
    csv_string = ""
    for row in grid_data:
        for entry in row:
            csv_string += str(entry) + ","
        # remove comma after the last entry in each row
        csv_string = csv_string[0:-1] + "\n"
    return csv_string


def _print_grid(grid_data, error_message):
    """ Print a 9 by 9 grid of numbers """
    print _grid_to_csv_string(grid_data, error_message)


def _grid_to_csv(grid_data, file_name, error_message):
    """
    Write a 9 by 9 grid of numbers
    to a file of comma separated values
    """
    try:
        file_handle = open(file_name, 'w')
        file_handle.write(_grid_to_csv_string(grid_data, error_message))
    except:
        exit("There was a problem writing to " + file_name)


def _affected_locations(row, column):
    """
    Return a 9 by 9 array that has ones in the row, column, and 3 by 3 region
    that contains the location specified by row and column.
    """
    affected_locations = numpy.zeros([9, 9], numpy.int)
    # add the modified row to the affected locations
    for i in range(9):
        affected_locations[row, i] = 1
    # add the modified column to the affected locations
    for i in range(9):
        affected_locations[i, column] = 1
    # add the modified region to the affected locations
    for i in numpy.array(range(3)) + 3*(row/3):
        for j in numpy.array(range(3)) + 3*(column/3):
            affected_locations[i, j] = 1
    # remove the modified location from the affected locations
        affected_locations[row, column] = 0
    return affected_locations


# Sudoku puzzle class
#
# Already written:
#     a method for reading csv files
#     a method for writing csv files
#     a method for printing Sudoku puzzles
#     a method for testing the validity of proposed solutions
#     a method to determine possible values for a position in the puzzle
#     a method for solving puzzles
#
# Not yet written:
#     a method for generating puzzles



################################################################################
# Main program
################################################################################

if __name__ == '__main__':

    PUZZLE_FILE_NAME = "insight_sudoku_puzzle.csv"
    sudoku_puzzle = Sudoku()
    sudoku_puzzle.puzzle_from_csv(PUZZLE_FILE_NAME)
    sudoku_puzzle.print_puzzle()
    print sudoku_puzzle._possibilities
    print
    sudoku_puzzle.print_solution()
    print sudoku_puzzle._valid_solution()
    print
    sudoku_puzzle.solve()
    sudoku_puzzle.print_solution()
    print sudoku_puzzle._possibilities
    print
    print sudoku_puzzle._valid_solution()
    sudoku_puzzle.write_solution_to_csv("my_solution.csv")
    exit()

    sudoku_puzzle.initialize_randomly()
    sudoku_puzzle.print_puzzle()
    exit()



