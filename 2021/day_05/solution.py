#!/usr/bin/env python3

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
def main():
    test_input = io.StringIO("""\
0,9 -> 5,9
8,0 -> 0,8
9,4 -> 3,4
2,2 -> 2,1
7,0 -> 7,4
6,4 -> 2,0
0,9 -> 2,9
3,4 -> 1,4
0,0 -> 8,8
5,5 -> 8,2
""")

    def parse_line(line):
        m = re.match(r"(\d+),(\d+) -> (\d+),(\d+)", line)
        if not m:
            raise ValueError("Unrecognized input: {line}")
        return map(lambda x: int(x), m.groups())

    with open("input.txt") as input_file:
        max_x = max_y = -math.inf
        for line in input_file:
            x0, x1, y0, y1 = parse_line(line)
            max_x = max(max(max_x, x0), x1)
            max_y = max(max(max_y, y0), y1)
    
        print(f"Got max x = {max_x}, max y = {max_y}.")
            
        input_file.seek(0, 0)
        
        grid = np.zeros((max_x + 1, max_y + 1), dtype='int')
        for line in input_file:
            line = line.strip()
            m = re.match(r"(\d+),(\d+) -> (\d+),(\d+)", line)
            if not m:
                raise ValueError("Unrecognized input: {line}")
            x0, y0, x1, y1 = map(lambda x: int(x), m.groups())
    
            print(f"Got line: {x0}, {y0} -> {x1}, {y1}")
    
            # only handle vertical and horizontal lines, for now
            if x0 == x1:
                y0, y1 = sorted([y0, y1])
                grid[y0:y1+1,x0] += 1
            elif y0 == y1:
                x0, x1 = sorted([x0, x1])
                grid[y0,x0:x1+1] += 1
            else:
                print("Line is not vertical or horizontal, skipped!")

    for r in grid:
        print(''.join([str(x) for x in r]).replace('0', '.'))

    # Count points where two or more lines overlap.
    print(
        f"There are {len(grid[grid >= 2])} points at least two lines overlap."
    )

if __name__ == "__main__":
    main()
