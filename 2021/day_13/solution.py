#!/usr/bin/env python3

import argparse
import numpy as np
import re

def print_paper(A):
    m = np.amax(A, axis=0)
    grid = np.full(m + 1, ".")
    for v in A:
        grid[tuple(v)] = "*"
    for r in grid:
        print(''.join(r))

def solve_part1(input_file):
    # parse lines to get inital state of "paper"
    coords = []
    folds = []
    for line in input_file:
        line = line.strip()

        print(line)

        if not line:
            # blank line
            continue
        elif line[0].isdigit():
            # this is a pair of coordinates
            coords.append([int(x) for x in line.split(",")])
        elif line.startswith("fold"):
            # this is a fold instruction
            m = re.match("fold along (x|y)=(\d+)", line)
            folds.append(m.groups())
        else:
            # skip unrecognized lines
            continue

    print(f"Got coords: {coords}.")
    print(f"Got folds:  {folds}.")

    # Set up array with 'dots'.
    A = np.array(coords)
    print(A)

    # Process folds.
    for axis, offset in folds:
        print(f"Processing fold on axis: {axis}, offset: {offset}.")

        dv = None
        if axis == "x":
            dv = A - [int(offset), 0]

            # don't change y axis values
            dv[:,1] = 0

            # if dx is negative, that indicates the point is on the
            # left side of the fold
            dv[dv[:,0] < 0] = 0
        elif axis == "y":
            dv = A - [0, int(offset)]

            # don't change x axis values
            dv[:,0] = 0

            # if dy is negative, that indicates the point is on the
            # top side of the fold
            dv[dv[:,1] < 0] = 0
        else:
            raise ValueError("Bad axis: {axis}")

        # Now apply the transform. Note that the transform is the
        # distance to the fold, so we need to double it here.
        # print(f"Applying transform: {dv}")
        A -= 2 * dv

        # Drop duplicate points.
        A = np.unique(A, axis=0)

        print_paper(A)
        print(f"{A.shape[0]} dots visible")

    # The letters appear to be sideways...
    print_paper(np.fliplr(A))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()
    solve_part1(args.input_file)

if __name__ == "__main__":
    main()
