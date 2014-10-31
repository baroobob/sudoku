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
    """
    Sudoku class for the Insight Data Engineering coding challenge
    """

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
        """ Read in Sudoku puzzle from a file of comma separated values """

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
        for row in range(9):
            for column in range(9):
                self.add_value_to_puzzle(data_list[row][column], row, column)


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


    def solve_puzzle(self):
        """
        Solve the Sudoku puzzle. Start by assigning the only possible value to
        all empty positions that have only one possibility. Then update
        possible_values and possibilities and call solve_puzzle again.
        """

        while self._there_are_empty_positions_with_one_possibility():
            for row in range(9):
                for column in range(9):
                    if self._possibilities == 1:
                        self._solution = self._possible_values[row][column][0]
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

def _print_grid(grid_data, error_message):
    """ Print a 9 by 9 grid of numbers """
    if grid_data.size != 81:
        exit(error_message)
    sudoku_string = ""
    for row in grid_data:
        for entry in row:
            sudoku_string += str(entry) + ","
        # remove comma after the last entry in each row
        sudoku_string = sudoku_string[0:-1] + "\n"
    print sudoku_string


def _grid_to_csv(grid_data, file_name, error_message):
    """
    Write a 9 by 9 grid of numbers
    to a file of comma separated values
    """
    if grid_data.size != 81:
        exit(error_message)
    csv_string = ""
    for row in grid_data:
        for entry in row:
            csv_string += str(entry) + ","
        # remove comma after the last entry in each row
        csv_string = csv_string[0:-1] + "\n"
    try:
        file_handle = open(file_name, 'w')
        file_handle.write(csv_string)
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


def _possible_values(grid_data, row_index, column_index):
    """
    Returns a list of the possible values a grid location can take without
    duplicating any of the values in its row, column, or 3 by 3 region.
    """

    if grid_data[row_index, column_index] == 0:
        possibilities = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    else:
        possibilities = grid_data[row_index, column_index]
    # remove the values in this row
    row = grid_data[row_index]
    for entry in row:
        if entry in possibilities:
            possibilities.remove(entry)

    # remove the values in this column
    column = numpy.transpose(grid_data)[column_index]
    for entry in column:
        if entry in possibilities:
            possibilities.remove(entry)

    # remove the values in this 3 by 3 region
    regions = list(
        grid_data[i:i + 3, j:j + 3] for i in [0, 3, 6] for j in [0, 3, 6])
    region_index = 3*(row_index/3) + column_index/3
    region = regions[region_index]
    region_entries = region.reshape(1, 9)[0]
    for entry in region_entries:
        if entry in possibilities:
            possibilities.remove(entry)

    print possibilities
    return possibilities


# write a Sudoku puzzle class that contains the following methods:
#     a method for reading csv files
#     a method for writing csv files
#     a method for printing Sudoku puzzles
#     a method for testing the validity of proposed solutions

#     a method for generating puzzles
#         a method to determine possible values for a position in the puzzle
#     a method for proposing solutions



################################################################################
# Main program
################################################################################

if __name__ == '__main__':

    PUZZLE_FILE_NAME = "insight_sudoku_puzzle.csv"
    SOLUTION_FILE_NAME = "insight_sudoku_solution.csv"
    sudoku_puzzle = Sudoku()
    sudoku_puzzle.puzzle_from_csv(PUZZLE_FILE_NAME)
    sudoku_puzzle.print_puzzle()
    print sudoku_puzzle._possibilities
    print
    sudoku_puzzle.print_solution()
    print sudoku_puzzle._valid_solution()
    exit()

    sudoku_puzzle.initialize_randomly()
    sudoku_puzzle.print_puzzle()
    exit()

    sudoku_solution = Sudoku()
    sudoku_solution.puzzle_from_csv(SOLUTION_FILE_NAME)
    sudoku_puzzle.print_puzzle()
    sudoku_solution.print_puzzle()
    sudoku_solution.write_solution_to_csv("my_solution.csv")


