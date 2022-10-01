#!/usr/bin/env python3

import argparse
import numpy as np
import sys

# Mess around with sys.path so we can import from our top-level.
sys.path.append("/Users/jcarreiro/src")

from advent_of_code.utils import read_array_from_file

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()

    # In this puzzle, we need to find the lowest cost path through a 2d array
    # (where the value at each index is the cost of visiting that index). This
    # is a straightforward application of Djikstra's algorithm.
    A = read_array_from_file(args.input_file)
    print(A)

    # This is the cost for each node, which we update as we visit the node's
    # neighbors. To start with, the cost for every node is infinity (ie. we
    # don't know how to get to that node yet).
    cost = np.full(A.shape, np.inf)

    # The cost for the start node is 0 (since we start there).
    cost[0,0] = 0    

    # Keep track of the nodes we've visited so far.
    visited = np.zeros(A.shape, dtype=bool)

    # Our current node.
    x = 0
    y = 0

    # Directions we can move at each node.
    directions = [
        # x   y
        ( 0, +1), # up
        (+1,  0), # right
        ( 0, -1), # down
        (-1,  0), # left
    ]

    def valid_move(y2, x2, shape):
        return y2 >= 0 and y2 < shape[0] and x2 >= 0 and x2 < shape[1]

    # We'll stop once we reach our target, or run out of nodes to consider.
    while not np.all(visited):
        # Get the next node to consider. Each iteration, we examine the
        # unvisited node with the lowest cost so far.
        M = np.ma.array(cost, mask=visited)
        idx = np.unravel_index(np.argmin(M, axis=None), M.shape)

        print(f"Got min cost index: {idx}.")
        
        # Compute the distance to each of our unvisited neighbors. If the
        # distance is shorter than the current best distance to the node,
        # update the cost for the node.
        y1, x1 = idx
        for dx, dy in directions:
            print(f"Checking direction: ({dx}, {dy}).")

            # Make sure we're not going out of bounds.
            x2 = x1 + dx
            y2 = y1 + dy
            if not valid_move(y2, x2, A.shape):
                print(f"Skipping out of bounds index: ({x2}, {y2}).")
                continue

            # ... and that we haven't already visited the node.
            if visited[y2, x2]:
                print(f"Skipping visited index: ({x2}, {y2}).")
                continue

            # The cost to reach each of our neighbors is now our cost (which by
            # definition is the minimum cost to reach _this_ node, since we
            # visit nodes in order of lowest cost) plus the cost of each node in
            # our original graph, or the cost already stored at the node (if
            # we've already visited another of the node's neighbors), whichever
            # is lower.
            c = cost[y1, x1] + A[y2, x2]
            print(f"cost[{y1}, {x1}] = {cost[y1, x1]}")
            print(f"A[{y2}, {x2}] = {A[y2, x2]}")
            print(f"Got new cost {c} for node at ({x2}, {y2}).")
            cost[y2, x2] = min(cost[y2, x2], c)
            print(f"Updated cost for node ({x2}, {y2}) is {cost[y2, x2]}.")
            print(cost)

        # We visited all the current node's neighbors, so mark it as visited.
        visited[idx] = True

    # The cost array now has the best path, which can be obtained by starting
    # at the end node and following the lowest cost neighbor at each step.
    best_path = []
    y1, x1 = A.shape
    y1 -= 1
    x1 -= 1
    while y1 != 0 or x1 != 0:
        best_path.append((y1, x1))
        next_y = None
        next_x = None
        min_cost = np.inf
        for dx, dy in directions:
            y2 = y1 + dy
            x2 = x1 + dx
            if valid_move(y2, x2, A.shape) and cost[y2, x2] < min_cost:
                next_y = y2
                next_x = x2
                min_cost = cost[y2, x2]
        y1 = next_y
        x1 = next_x
    best_path.append((0, 0))
    print(list(reversed(best_path)))

    # Print the array showing the best path, just for fun.
    for y in range(A.shape[0]):
        for x in range(A.shape[1]):
            if (y, x) in best_path:
                BOLD = "\033[1m"
                END = "\033[0m"
            else:
                BOLD = ""
                END = ""
            print(f"{BOLD}{A[y,x]}{END}", end="")
        print()

    # Print the cost of the end node (the risk on the lowest total risk path).
    print(f"Lowest risk path total cost is {cost[-1,-1]}.")
            
if __name__ == "__main__":
    main()
