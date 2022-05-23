#!/usr/bin/env python3

import argparse
import io
import math
import numpy as np
import re

# In this problem, we're given lists of horizontal and vertical lines, in the
# form: x0,y0 -> x1,y1 (where either x0 == x1 or y0 == y1 by definition.)
# We need to find all the points where two or more lines overlap.
#
# To do this, we're just going to "draw" the lines onto a grid. This will
# have the side benefit that we can print out the grid when we're done!

def solve(infile, handle_diagonals=True):
    def parse_line(line):
        m = re.match(r"(\d+),(\d+) -> (\d+),(\d+)", line)
        if not m:
            raise ValueError("Unrecognized input: {line}")
        return map(lambda x: int(x), m.groups())

    max_x = max_y = -math.inf
    for line in infile:
        x0, x1, y0, y1 = parse_line(line)
        max_x = max(max(max_x, x0), x1)
        max_y = max(max(max_y, y0), y1)
        
    print(f"Got max x = {max_x}, max y = {max_y}.")
            
    infile.seek(0, 0)
        
    grid = np.zeros((max_x + 1, max_y + 1), dtype='int')
    for line in infile:
        line = line.strip()
        m = re.match(r"(\d+),(\d+) -> (\d+),(\d+)", line)
        if not m:
            raise ValueError("Unrecognized input: {line}")
        x0, y0, x1, y1 = map(lambda x: int(x), m.groups())

        print(f"Got line: {x0}, {y0} -> {x1}, {y1}")

        # In part one, we only needed to consider horizontal and vertical
        # lines. For part two, we also need to handle diagonals. Note that
        # the problem stipulates the diagonals will only ever be at a 45
        # degree angle (ie. they have slope 1).
        if x0 == x1:
            y0, y1 = sorted([y0, y1])
            grid[y0:y1+1,x0] += 1
        elif y0 == y1:
            x0, x1 = sorted([x0, x1])
            grid[y0,x0:x1+1] += 1
        else:
            if handle_diagonals:
                rx = np.arange(x0, x1 + 1) if x0 < x1 else np.arange(x0, x1 - 1, -1)
                ry = np.arange(y0, y1 + 1) if y0 < y1 else np.arange(y0, y1 - 1, -1)
                grid[ry, rx] += 1
            else:
                print("Line is not vertical or horizontal, skipped!")

    for r in grid:
        print(''.join([str(x) for x in r]).replace('0', '.'))

    # Count points where two or more lines overlap.
    print(
        f"There are {len(grid[grid >= 2])} points at least two lines overlap."
    )


def main(handle_diagonals=True):
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=argparse.FileType())
    args = parser.parse_args()
    solve(args.infile)

    
if __name__ == "__main__":
    main()
