#!/usr/bin/env python3

import math
import numpy as np

def solve_part1(input_list, phases):
    base_pattern = [0, 1, 0, -1]
    rows = []
    # We're going to have as many rows as their are numbers in our input list.
    for i in range(len(input_list)):
        # TODO: repeat elements for 2nd, etc. input
        pattern = []
        for x in base_pattern:
            pattern += [x] * (i + 1)

        # Note that he plus 1 here is because we shift the whole pattern left
        # once.
        input_len = len(input_list) + 1

        # Copy pattern enough times to cover whole input sequence.
        n = math.ceil(input_len / len(pattern))
        if n > 1:
            pattern = pattern * n
        rows.append(pattern[1:input_len])

    # M is the input matrix.
    M = np.array([input_list] * len(input_list))
    print(f"M has dimensions {M.shape}.")

    # N is the "pattern matrix".
    N = np.array(rows)
    print(f"N has dimensions {N.shape}.")

    # Note that the problem only asks us to input the first 8 digits of the
    # answer, so we only need the first 8 rows of the input and the first
    # 8 columns of the pattern matrix.
    # M = M[0:8,:]
    # N = N[0:8,:]

    # Now we apply the pattern matrix for P phases to get our output.
    for phase in range(phases):
        print(f"Processing phase {phase}.")
        M = np.mod(np.abs(np.dot(M, N.T)), 10)
        print(M)
    return M[0:1,:].flatten().tolist()

if __name__ == "__main__":
    # This is the first example in the problem. After 4 phases, the output
    # should be 0, 1, 0, 2, 9, 4, 9, 8.
    example_1 = list(range(1, 9))

    # This is the second example. After 100 phases, the first eight digits
    # of the output should be 2, 4, 1, 7, 6, 1, 7, 6.
    example_2 = [8, 0, 8, 7, 1, 2, 2, 4, 5, 8, 5, 9, 1, 4, 5, 4, 6, 6, 1, 9, 0,
                 8, 3, 2, 1, 8, 6, 4, 5, 5, 9, 5]

    def make_number_list(s):
        return [int(d) for d in s]

    # "19617804207202209144916044189917 becomes 73745418" after 100 phases.
    example_3 = make_number_list("19617804207202209144916044189917")

    # "69317163492948606335995924319873 becomes 52432133" after 100 phases.
    example_4 = make_number_list("69317163492948606335995924319873")

    def read_number_list(filename):
        with open(filename, "r") as f:
            return make_number_list(f.readline().strip())

    output = solve_part1(read_number_list("input"), 100)
    print(''.join([str(x) for x in output]))
