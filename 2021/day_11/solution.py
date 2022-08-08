#!/usr/bin/env python3

import argparse
import itertools
import numpy as np

import sys

# Mess around with sys.path so we can import from our top-level.
sys.path.append("/Users/jcarreiro/src")

from advent_of_code.utils import read_array_from_file

# In this problem, we're given an array of "octopuses", each of which has an
# energy level from 0 to 9. Every time step, the energy level of each octopus
# increases by one; then, any octopus with an energy level greater than 9
# "flashes", which further increases the energy level of all the surrounding
# octopus (including diagonally adjacent) by one. Note that each octopus can
# only flash once per time step, regardless of how much energy it ends up with.
# Finally, the energy level of all the octopus who flashed is reset to 0.
#
# To solve the problem, we need to simulate 100 steps of this process and count
# the total number of flashes we see.
def solve_part1(input_file):
    # Read in the array of initial energy levels.
    A = read_array_from_file(input_file)
    print(A)

    # Simulate 100 timesteps and count the flashes we see.
    flashes = 0
    for t in range(1,101):
        print(f"Running timestamp {t}.")

        # First we need to increase the energy level of all octopus by 1.
        A += 1

        # print(A)

        # We'll use this array to track which octopus already flashed on
        # this time step.
        flashed = np.zeros(A.shape, dtype=bool)

        # Now we need to flash all of the octopus with an energe level greater
        # than 9. Note that the flashing can cause a nearby octopus to end up
        # with more than 9 energy, and then it will flash too.
        while np.any((A > 9) & ~flashed):
            # Grab a random octopus with more than 9 energy that hasn't
            # flashed yet.
            i, j = np.argwhere((A > 9) & ~flashed)[0]

            # print(f"Got index: ({i}, {j}).")

            # Flash it.
            flashed[i][j] = True
            flashes += 1

            # Increment the energy level of any neighbors. Note that this
            # product includes (0,0) but we don't care since by definition,
            # that octopus already flashed.
            for di, dj in itertools.product([-1, 0, 1], [-1, 0, 1]):
                i2, j2 = i + di, j + dj        
                if i2 >= 0 and i2 < A.shape[0] and j2 >= 0 and j2 < A.shape[1]:
                    # print(f"Increasing energy at index ({i2}, {j2}).")
                    A[i2][j2] += 1

        # Reset all flashed octopus to 0 energy.
        A[flashed] = 0

        # print(A)
        # print(A.shape)

        # Print the output of this time step.
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                if flashed[i][j]:
                    BOLD = "\033[1m"
                    END = "\033[0m"
                else:
                    BOLD = ""
                    END = ""
                print(f"{BOLD}{A[i][j]}{END}", end="")
            print()

    print(f"Got {flashes} flashes in {t} time steps.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()
    solve_part1(args.input_file)

if __name__ == "__main__":
    main()
