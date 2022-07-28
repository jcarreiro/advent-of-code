#!/usr/bin/env python3

import argparse
import numpy as np
import scipy.ndimage

def solve_part1(input_file):
    # Read the input file into an ndarray.
    l = []
    for line in input_file:
        l.append([int(x) for x in line.strip()])
    A = np.array(l)

    # Find the minimum neighbor for each element. We can use a convolution here.
    #
    # For some reason, using cval=np.inf doesn't work here (though it should,
    # since every value in the array is less than +inf). Since the digits will
    # always be in the range 0-9, using a cval of 100 should be safe.
    M = scipy.ndimage.minimum_filter(
        A,
        footprint=np.array(
            [
                [0, 1, 0],
                [1, 0, 1],
                [0, 1, 0],
            ],
        ),
        mode='constant',
        cval=100,
    )

    # Finally compute the mask that tells us if each element is a "low point".
    m = A < M

    # Print the input with the minimums bolded, like the example on the web
    # page.
    #
    # This is the standard escape sequence for bold text.
    BOLD = "\033[1m"

    # This is the sequence used to reset terminal state.
    END = "\033[0m"

    last_row = 0
    for idx, x in np.ndenumerate(A):
        row, col = idx
        if row > last_row:
            print()
            last_row = row
        if m[row][col]:
            print(f"{BOLD}{x}{END}", end="")
        else:
            print(f"{x}", end="")
    print()

    # Now print the answer, which is the sum of "risk levels" (one plus the
    # height for each low point).
    print(np.sum(A[m] + 1))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()
    solve_part1(args.input_file)

if __name__ == "__main__":
    main()
