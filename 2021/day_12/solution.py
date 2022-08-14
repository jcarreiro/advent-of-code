#!/usr/bin/env python3

import argparse
import copy

from collections import defaultdict, deque

def find_paths(G, is_valid_move):
    # BFS through the graph to find all the paths to the end. Note that:
    #
    #   - we can't go back to the start or leave the end node
    #   - we can't visit 'small' caves more than once (except in part 2, where
    #     we can visit a single small cave twice)
    #   - we can visit 'big' caves any number of times (cycles?)
    #
    # Our output is the list of all the paths.
    paths = []
    queue = deque([(("start",), {})])
    while queue:
        # The basic idea here is to pull a partial path off of the queue
        # and create new paths from it by appending all legal next moves.
        # If any of those paths have reached the 'end' node, they can be
        # added to our list of paths; otherwise they can be put back on
        # the queue to be extended again.
        #
        # Get the first path in our queue.
        path, extra = queue.popleft()

        # Check the neighbors of the last node on the path to see how we
        # may be able to extend it.
        p = path[-1]
        for q in G[p]:
            # Note that we need to make a copy here so that subsequent
            # iterations don't see the changes made while testing this
            # node.
            extra_copy = copy.deepcopy(extra)
            if q == 'start':
                # can't go back to start
                continue
            elif q == 'end':
                # reached end, append path to valid paths
                paths.append(path + ('end',))
                continue
            elif not is_valid_move(path, q, extra_copy):
                continue

            # if we get here, this is a valid extension to the path
            queue.append((path + (q,), extra_copy))

    # Queue is empty -> we've found all paths to end
    return paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()

    # Parse the input file and build the graph.
    #
    # We expect the lines to look like:
    #
    #   line := cave '-' cave
    #   cave := 'start' | 'end' | uppercase_letter | lowercase_letter
    #
    # We use a simple adjacency list representation to store our graph.
    G = defaultdict(list)
    for line in args.input_file:
        line = line.strip()
        f, t = line.split("-")
        print(f"Found edge: {f} - {t}")
        G[f].append(t)
        G[t].append(f)

    # TODO: print a nice graphical representation of the graph
    print(f"Got graph: {G}")

    # For part one, we can't repeat any small cave in the path.
    paths = find_paths(
        G,
        lambda path, q, _: not q.islower() or (q.islower() and not q in path),
    )

    print("PART ONE")
    print("--------")
    print(f"Found {len(paths)} paths from start to end.")
    print("Paths:")
    for path in paths:
        print(f"  {','.join(path)}")

    # For part two, we can use one small cave twice.
    def is_valid_move_part2(path, cave, extra):
        if cave.isupper():
            # cave is big => valid
            return True
        else:
            # cave is small but haven't used any small cave twice => valid
            #
            # Make sure our extra data is set up correctly.
            if not "visited" in extra:
                extra["visited"] = defaultdict(int)
            if not "visited_twice" in extra:
                extra["visited_twice"] = False

            if extra["visited"][cave] == 0:
                # We haven't visited this small cave yet.
                extra["visited"][cave] = 1
                return True
            elif extra["visited"][cave] == 1 and not extra["visited_twice"]:
                # We visited this small cave once, but we can still visit a
                # small cave twice.
                extra["visited"][cave] = 2
                extra["visited_twice"] = True
                return True
            else:
                # We can't visit this small cave again.
                return False


    paths = find_paths(G, is_valid_move_part2)

    print("PART TWO")
    print("--------")
    print(f"Found {len(paths)} paths from start to end.")
    print("Paths:")
    for path in paths:
        print(f"  {','.join(path)}")


if __name__ == "__main__":
    main()
