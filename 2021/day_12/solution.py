#!/usr/bin/env python3

import argparse

from collections import defaultdict, deque

def solve_part1(input_file):
    # parse input file and build graph
    #
    # we expect the lines to look like:
    #
    #   line := cave '-' cave
    #   cave := 'start' | 'end' | uppercase_letter | lowercase_letter
    #
    # We use a simple adjacency list representation to store our graph.
    G = defaultdict(list)
    for line in input_file:
        line = line.strip()
        f, t = line.split("-")
        print(f"Found edge: {f} - {t}")
        G[f].append(t)
        G[t].append(f)

    # TODO: print a nice graphical representation of the graph
    print(f"Got graph: {G}")

    # BFS through the graph to find all the paths to the end. Note that:
    #
    #   - we can't go back to the start or leave the end node
    #   - we can't visit 'small' caves more than once
    #   - we can visit 'big' caves any number of times (cycles?)
    #
    # Our output is the list of all the paths.
    paths = []
    queue = deque([("start",)])
    while queue:
        # The basic idea here is to pull a partial path off of the queue
        # and create new paths from it by appending all legal next moves.
        # If any of those paths have reached the 'end' node, they can be
        # added to our list of paths; otherwise they can be put back on
        # the queue to be extended again.
        #
        # Get the first path in our queue.
        path = queue.popleft()
        print(f"Considering path: {path}.")

        # Check the neighbors of the last node on the path to see how we
        # may be able to extend it.
        p = path[-1]
        for q in G[p]:
            if q == 'start':
                # can't go back to start
                continue
            elif q == 'end':
                # reached end, append path to valid paths
                paths.append(path + ('end',))
                continue
            elif q.islower() and q in path:
                # can't go back to 'small' caves; this also
                # prunes dead end paths
                continue

            # if we get here, this is a valid extension to the path
            queue.append(path + (q,))

    # Queue is empty -> we've found all paths to end
    print(f"Found {len(paths)} paths from start to end.")
    print("Paths:")
    for path in paths:
        print(f"  {','.join(path)}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()
    solve_part1(args.input_file)

if __name__ == "__main__":
    main()
