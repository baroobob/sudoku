""" Sudoku solver for the Insight Data Engineering coding challenge """
# written for Python 2.7.8

# import required libraries
import csv
import numpy


def sudoku_from_csv(file_name):
    """ read in csv representing Sudoku puzzle """
    error_message = file_name + \
    "does not appear to be a valid 9 by 9 Sudoku puzzle"
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
    if len(data_list != 81):
        exit(error_message)
    data = numpy.array(data_list)
    return data

def valid_sudoku_solution(data):
    """ test the validity of a proposed Sudoku solution """
    # check rows
    for row in data:
        for entry in row:
            # all entries must be 1-9
            if entry not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                return False
            # all entries in a row must be unique
            if sum(list(int(i == entry) for i in row)) > 1:
                return False

    # check columns
    for column in numpy.transpose(data):
        for entry in column:
            # all entries must be 1-9
            if entry not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                return False
            # all entries in a row must be unique
            if sum(list(int(i == entry) for i in column)) > 1:
                return False

    # check 3 by 3 regions
    regions = list(data[i:i+3, j:j+3] for i in [0, 3, 6] for j in [0, 3, 6])
    for region in regions:
        region_entries = region.reshape(1, 9)[0]
        for entry in region_entries:
            # all entries must be 1-9
            if entry not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                return False
            # all entries in a region must be unique
            if sum(list(int(i == entry) for i in region_entries)) > 1:
                return False

    return True


# decide on a strategy for producing proposed solutions

if __name__ == '__main__':
    #FILE_NAME = "sudoku_puzzle.csv"
    FILE_NAME = "sudoku_solution.csv"
    sudoku_puzzle = sudoku_from_csv(FILE_NAME)
    print sudoku_puzzle
    print

    
    #for i,region in enumerate(regions):
        #print "Region", i 
        #print region

    print valid_sudoku_solution(sudoku_puzzle)

