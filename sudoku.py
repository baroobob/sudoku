"""
Sudoku class for the Insight Data Engineering coding challenge.
This class contains methods for generating and solving Sudoku puzzles as well
as methods for reading and writing puzzles and solutions to and from csv files.

Author: Jim Bridgewater
Written for Python 2.7.8
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
        """
        Sudoku class constructor that initializes arrays for the puzzle, the
        puzzle's solution, and other internal data structures used to create
        and solve Sudoku puzzles.
        """

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


    def _get_possible_values(self, location):
        """
        Returns a list of possible values for a location in the Sudoku grid and
        provides indexing with tuples.
        """
        row = location[0]
        column = location[1]
        return self._possible_values[row][column]


    def _rows(self):
        """
        Return a list of nine arrays which contain the entries in each of
        the nine rows in the solution to the Sudoku puzzle.
        """
        rows = list(row for row in self._solution)
        return rows


    def _columns(self):
        """
        Return a list of nine arrays which contain the entries in each of
        the nine columns in the solution to the Sudoku puzzle.
        """
        columns = list(column for column in numpy.transpose(self._solution))
        return columns


    def _regions(self):
        """
        Return a list of nine arrays which contain the entries in each of
        the nine 3 by 3 regions in the solution to the Sudoku puzzle.
        """
        regions = list(
            self._solution[i:i+3, j:j+3] for i in [0, 3, 6] for j in [0, 3, 6])
        for i in range(9):
            regions[i] = regions[i].reshape(1, 9)[0]
        return regions


    def puzzle_from_csv(self, file_name):
        """ Read a Sudoku puzzle from a file of comma separated values. """

        try:
            file_handle = open(file_name)
            csvreader = csv.reader(file_handle, skipinitialspace=True)
            data_list = []
            for line in csvreader:
                row = list(int(i) for i in line)
                assert len(row) == 9, "wrong number of columns in " + file_name
                data_list.append(row)
        except:
            exit("There was a problem reading " + file_name)
        assert len(data_list) == 9, "wrong number of rows in " + file_name
        self._puzzle = numpy.array(data_list)
        self._solution = numpy.array(data_list)
        self._update_possible_values()
        print "Sudoku puzzle read from " + file_name


    def _update_possible_values(self):
        """
        Updates all entries in _possible_values and _possibilities
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
            # this location already contains a value, no more choices
            possible_values = []
        else:
            # this location is empty
            possible_values = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        constraining_locations = _constraining_locations(row, column)
        for i in range(9):
            for j in range(9):
                if constraining_locations[i, j] == 1:
                    # remove values found in the row, column and region
                    value = self._solution[i, j]
                    if value in possible_values:
                        possible_values.remove(value)
        return possible_values


    def print_puzzle(self):
        """ Print the Sudoku puzzle. """
        print
        print "Sudoku puzzle:"
        print
        _print_grid(self._puzzle)


    def print_solution(self):
        """ Print the Sudoku puzzle's solution. """
        if self._valid_solution():
            print
            print "Sudoku solution:"
            print
            _print_grid(self._solution)
        else:
            print "The Sudoku puzzle has not been solved!"


    def write_puzzle_to_csv(self, file_name):
        """ Write the Sudoku puzzle to a file of comma separated values. """
        _grid_to_csv(self._puzzle, file_name)
        print "Puzzle written to " + file_name


    def write_solution_to_csv(self, file_name):
        """
        Write the Sudoku puzzle's solution to a file of comma separated values.
        """
        if self._valid_solution():
            _grid_to_csv(self._solution, file_name)
            print "Solution written to " + file_name
        else:
            error_message = "Data for " + file_name + \
            " is not a valid Sudoku solution."
            exit(error_message)


    def _valid_solution(self):
        """ Test the validity of a proposed Sudoku solution. """
        # check rows
        for row in self._rows():
            for entry in row:
                # all entries must be 1-9
                if entry not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    return False
                # all entries in a row must be unique
                if sum(list(int(i == entry) for i in row)) > 1:
                    return False

        # check columns
        for column in self._columns():
            for entry in column:
                # all entries must be 1-9
                if entry not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    return False
                # all entries in a column must be unique
                if sum(list(int(i == entry) for i in column)) > 1:
                    return False

        # check 3 by 3 regions
        for region in self._regions():
            for entry in region:
                # all entries must be 1-9
                if entry not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    return False
                # all entries in a region must be unique
                if sum(list(int(i == entry) for i in region)) > 1:
                    return False

        return True


    def solve(self, verbose=True):
        """ Solve the Sudoku puzzle. """
        """
        Start by searching for empty locations that have only one possible
        value. If any are found, add the only possible value in those
        locations and update possible_values. Then look for numbers that are
        possible values in a single row, column, or region location.  Add
        those values and update possible_values.  Repeat this process until
        nothing more is found.
        """
        if not self._puzzle_solvable():
            print "This is not a valid Sudoku puzzle and cannot be solved!"
            return False

        keep_going = True
        while keep_going:
            keep_going = False

            # enter numbers in locations that have only one possible value
            for i in range(9):
                for j in range(9):
                    if self._possibilities[i][j] == 1:
                        # found a location with only one possible value
                        keep_going = True
                        only_possible_value = self._possible_values[i][j][0]
                        self._solution[i][j] = only_possible_value
                        if verbose:
                            print "Adding", only_possible_value,
                            print "at row", i + 1, "column", j + 1,
                            print "- only possible value for this location"
            self._update_possible_values()

            # enter numbers that are possible values in a single location
            # in a 3 by 3 region
            for region in range(9):
                # for each region build a list of possible values
                locations = []
                region_list = []
                for row in _region_row_range(region):
                    for column in _region_column_range(region):
                        locations.append((row, column))
                        possible_values = self._possible_values[row][column]
                        region_list.extend(possible_values)
                # if a number is in the list only once add it
                # in the only location possible
                for number in range(1,10):
                    if region_list.count(number) == 1:
                        # found a number that can only go in one location
                        keep_going = True
                        for location in locations:
                            possible_values = self._get_possible_values(location)
                            if number in possible_values:
                                self._solution[location] = number
                                if verbose:
                                    print "Adding", number, 
                                    print "at row", location[0] + 1,
                                    print "column", location[1] + 1,
                                    print "- only possible location for this",
                                    print "value in region"
            self._update_possible_values()

            # enter numbers that are possible values in a
            # single location in a row
            for row in range(9):
                # for each row build a list of possible values so we can see
                # how many times each number occurs
                locations = []
                row_list = []
                row_lists = []
                for column in range(9):
                    locations.append((row, column))
                    possible_values = self._possible_values[row][column]
                    row_list.extend(possible_values)
                # if a number is in the list only once add it
                # in the only location possible
                for number in range(1,10):
                    if row_list.count(number) == 1:
                        # found a number that can only go in one location
                        keep_going = True
                        for location in locations:
                            possible_values = self._get_possible_values(location)
                            if number in possible_values:
                                self._solution[location] = number
                                if verbose:
                                    print "Adding", number, 
                                    print "at row", location[0] + 1,
                                    print "column", location[1] + 1,
                                    print "- only possible location for this",
                                    print "value in row"
            self._update_possible_values()


            # enter numbers that are possible values in a
            # single location in a column
            for column in range(9):
                # for each column build a list of possible values so we can see
                # how many times each number occurs
                locations = []
                column_list = []
                for row in range(9):
                    locations.append((row, column))
                    possible_values = self._possible_values[row][column]
                    column_list.extend(possible_values)
                # if a number is in the list only once add it
                # in the only location possible
                for number in range(1,10):
                    if column_list.count(number) == 1:
                        # found a number that can only go in one location
                        keep_going = True
                        for location in locations:
                            possible_values = self._get_possible_values(location)
                            if number in possible_values:
                                self._solution[location] = number
                                if verbose:
                                    print "Adding", number, 
                                    print "at row", location[0] + 1,
                                    print "column", location[1] + 1,
                                    print "- only possible location for this",
                                    print "value in column"
            self._update_possible_values()

        if 0 in self._solution:
            # there are still empty locations in the solution
            if verbose:
                print
                print "Unable to completely solve this Sudoku puzzle!"
                print
                print "This is as far as I got:"
                print
                _print_grid(self._solution)
            return False
        else:
            return True


    def new_puzzle(self):
        """ Generate a new Sudoku puzzle. """
        """
        Do this by generating a new solution from scratch and then removing
        numbers to make a puzzle.
        """
        print "Generating a new Sudoku puzzle"
        self._new_solution()

        # remove numbers from the solution until the puzzle is unsolvable
        locations = [(i, j) for i in range(9) for j in range(9)]
        solvable = True
        while solvable:
            location = random.choice(locations)
            last_number_removed = self._solution[location]
            self._puzzle[location] = 0
            # have to update solution too to loop with solve()
            self._solution[:,:] = self._puzzle[:,:]
            self._update_possible_values()
            locations.remove(location)
            solvable = self.solve(verbose=False)
            
        # put back the last number removed so the puzzle can be solved
        self._puzzle[location] = last_number_removed
        self._solution[:,:] = self._puzzle[:,:]
        self._update_possible_values()
        

    def _new_solution(self):
        """ Generate a Sudoku solution from scratch. """
        self.__init__()
        row = 0
        while row < 9:
            column = 0
            while column < 9:
                # enter one of the possible values in this location
                possible_values = self._possible_values[row][column]
                self._puzzle[row, column] = random.choice(possible_values)
                self._solution[row, column] = self._puzzle[row, column]
                self._update_possible_values()
                if self._puzzle_solvable():
                    # the puzzle is still solvable so move to the next location
                    column = column + 1
                else:
                    # the puzzle has become unsolvable so retry this row
                    for column in range(9):
                        self._puzzle[row, column] = 0
                        self._solution[row, column] = 0
                    self._update_possible_values()
                    column = 0
            row = row + 1


    def _puzzle_solvable(self):
        """
        Determine if the puzzle has a solution by ensuring that
        there is a unique value available for every location in
        each row, column, and region.
        """

        # check the rows to make sure there is still a unique choice available
        # for each empty location in the row
        for row in range(9):
            row_lists = self._possible_values[row]
            row_lists = [
                self._possible_values[row][column]
                for column in range(9)
                if self._solution[row][column] == 0
            ]
            if not _unique_choice(row_lists):
                return False

        # check the regions to make sure there is still a unique choice
        # available for each empty location in the region
        for region in range(9):
            region_lists = [
                self._possible_values[row][column]
                for row in _region_row_range(region)
                for column in _region_column_range(region)
                if self._solution[row][column] == 0
            ]
            if not _unique_choice(region_lists):
                return False

        # check the columns to make sure there is still a unique choice
        # available for each empty location in the column
        for column in range(9):
            column_lists = [
                self._possible_values[row][column]
                for row in range(9)
                if self._solution[row][column] == 0
            ]
            if not _unique_choice(column_lists):
                return False

        return True


################################################################################
# Function definitions
################################################################################

def _region_row_range(region_number):
    """
    Returns a list of the rows that intersect the region specified by
    the integer region_number.  The regions are numbered 0-8 from top left
    to bottom right.
    """
    starting_row = 3*(region_number/3)
    return range(starting_row, starting_row + 3)


def _region_column_range(region_number):
    """
    Returns a list of the columns that intersect the region specified by
    the integer region_number.  The regions are numbered 0-8 from top left
    to bottom right.
    """
    starting_column = 3*(region_number % 3)
    return range(starting_column, starting_column + 3)


def _grid_to_csv_string(grid_data):
    """
    Make a string of comma separated values from a 9 by 9 grid of numbers
    """
    assert grid_data.size == 81
    csv_string = ""
    for row in grid_data:
        for entry in row:
            csv_string += str(entry) + ","
        # remove comma after the last entry in each row
        csv_string = csv_string[0:-1] + "\n"
    return csv_string


def _print_grid(grid_data):
    """ Print a 9 by 9 grid of numbers """
    print _grid_to_csv_string(grid_data)


def _grid_to_csv(grid_data, file_name):
    """
    Write a 9 by 9 grid of numbers
    to a file of comma separated values
    """
    try:
        file_handle = open(file_name, 'w')
        file_handle.write(_grid_to_csv_string(grid_data))
    except:
        exit("There was a problem writing to " + file_name)


def _constraining_locations(row, column):
    """
    Return a 9 by 9 array that has ones in the row, column, and 3 by 3 region
    surrounding the location specified by row and column.
    """
    constraining_locations = numpy.zeros([9, 9], numpy.int)
    # add locations in the row to the constraining locations
    for i in range(9):
        constraining_locations[row, i] = 1
    # add locations in the column to the constraining locations
    for i in range(9):
        constraining_locations[i, column] = 1
    # add locations in the region to the constraining locations
    for i in numpy.array(range(3)) + 3*(row/3):
        for j in numpy.array(range(3)) + 3*(column/3):
            constraining_locations[i, j] = 1
    # remove the location itself from the constraining locations
    constraining_locations[row, column] = 0
    return constraining_locations


def _unique_choice(list_of_lists):
    """
    Determine if unique values can be chosen from a group of sets. In general
    this is a rather challenging / computationally intensive problem, but for
    generating Sudoku puzzles we only start to run into problems when the
    choices are narrowed down to one or two.
    """
    sizes = [len(set(l)) for l in list_of_lists]

    # if any set has 0 members return false
    if 0 in sizes:
        return False

    # if the union of sets containing a single number has fewer members than
    # the number of these sets then at least two of these sets contain the same
    # number and unique values cannot be chosen from each set
    sets_in_union = 0
    union_of_sets = set([])
    for i, size in enumerate(sizes):
        if size == 1:
            sets_in_union = sets_in_union + 1
            union_of_sets = union_of_sets.union(set(list_of_lists[i]))
            if len(union_of_sets) < sets_in_union:
                return False

    # if the union of sets with 1 or 2 members has fewer members than
    # the number of these sets then there is no solution
    for i, size in enumerate(sizes):
        if size == 2:
            sets_in_union = sets_in_union + 1
            union_of_sets = union_of_sets.union(set(list_of_lists[i]))
            if len(union_of_sets) < sets_in_union:
                return False

    return True



################################################################################
# Main program
################################################################################

if __name__ == '__main__':

    SUDOKU = Sudoku()

    SUDOKU.new_puzzle()
    SUDOKU.print_puzzle()
    SUDOKU.solve()
    SUDOKU.print_solution()

    PUZZLE_FILE_NAME = "insight_sudoku_puzzle.csv"
    SUDOKU.puzzle_from_csv(PUZZLE_FILE_NAME)
    SUDOKU.print_puzzle()
    SUDOKU.solve()
    SUDOKU.print_solution()
    SUDOKU.write_solution_to_csv("my_solution.csv")

