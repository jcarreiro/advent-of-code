#!/usr/bin/env python3

import argparse
import numpy as np
import scipy.ndimage

# Read the input file into an ndarray.
def read_input(input_file):    
    l = []
    for line in input_file:
        l.append([int(x) for x in line.strip()])
    return np.array(l)

def solve_part1(input_file):
    A = read_input(input_file)

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

def solve_part2(input_file):
    # In part 2, we need to find the largest "basins" (all elements which flow
    # "down" to a low point). '9's are not considered to be part of any basin,
    # and every other number is part of a single basin, so we can just pick
    # random points on the grid and search from that point, stopping when we hit
    # a '9'. Once we've explored every point, we'll have a list of the biggest
    # basins.
    #
    # If we need to make this faster, we can also stop the search as soon as the
    # list of unexplored points is smaller than our 3rd largest basin; at that
    # point, no remaining basin can be in the top 3, and we only need to find
    # the top 3 to solve the problem.
    A = read_input(input_file)
    print(A)

    # Set up an array of flags to use for marking nodes as visited.
    # 
    # We mark all '9's as visited here, since (1) we never want to actually
    # count them as part of a basin and (2) there's no point to starting from a
    # '9' in our search anyway.
    visited = A == 9
    print(visited)

    # Now we're ready to search.
    #
    # We only need the sizes to solve the problem, so that's all we're going to
    # store.
    basin_sizes = []
    while not np.all(visited):
        # There are unvisited nodes left. Grab a random unvisited node.
        y, x = np.argwhere(visited != True)[0]

        print(f"Searching from point: {(x,y)}.")

        def dfs(A, visited, x, y):
            print(f"> Visiting point: {(x,y)}.")

            assert(not visited[y][x])

            # Mark this node as visited.
            visited[y][x] = True

            # Our basin size is at least one since we're a valid visted node.
            basin_size = 1

            # Try to visit each neighbor: up, down, left, right.
            DIRECTIONS = [(0, 1), (0, -1), (-1, 0), (1, 0)]
            for dx, dy in DIRECTIONS:
                x1, y1 = x + dx, y + dy

                print(f">> Checking point: {(x1, y1)}.")

                if x1 < 0 or x1 >= A.shape[1] or y1 < 0 or y1 >= A.shape[0]:
                    # Don't walk off the edge of the map.
                    print(f">>> Point {(x1, y1)} is off edge!")
                    continue
                elif visited[y1][x1]:
                    # Don't revisit a node we've already visited.
                    print(f">>> Point {(x1, y1)} was already visited!")
                    continue
                else:
                    basin_size += dfs(A, visited, x1, y1)

            return basin_size
        
        basin_size = dfs(A, visited, x, y)
        
        print(f"Found basin of size: {basin_size}.")
        
        basin_sizes.append(basin_size)

    # Now print the list of basin sizes.
    print(f"Basin sizes: {basin_sizes}.")

    # We should have gotten at least 3 basins, per the problem definition.
    assert(len(basin_sizes) >= 3)

    # The answer is the product of the three largest sizes.
    print(f"Got product: {np.prod(sorted(basin_sizes, reverse=True)[:3])}.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()
    solve_part2(args.input_file)

if __name__ == "__main__":
    main()
