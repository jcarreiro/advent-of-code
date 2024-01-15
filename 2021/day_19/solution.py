#!/usr/bin/env python3

import itertools
import numpy as np
import re

from collections import defaultdict
from functools import reduce

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)


# Note that our coordinate system is +x to the right, +y up.
class Bounds:
    def __init__(self, bottom, left, top, right):
        self.bottom = bottom
        self.left = left
        self.top = top
        self.right = right

    def __repr__(self):
        return f"Bounds(bottom={self.bottom}, left={self.left}, top={self.top}, right={self.right})"

    def __eq__(self, other):
        return (
            self.bottom == other.bottom and
            self.left == other.left and
            self.top == other.top and
            self.right == other.right
        )

    @staticmethod
    def get_bounds(points):
        p = points[0]
        b = Bounds(p.y, p.x, p.y, p.x)
        for p in points[1:]:
            b.extend(p)
        return b

    @staticmethod
    def empty():
        return Bounds(np.inf, np.inf, -np.inf, -np.inf)

    def extend(self, p):
        self.bottom = min(self.bottom, p.y)
        self.left = min(self.left, p.x)
        self.top = max(self.top, p.y)
        self.right = max(self.right, p.x)

    def union(self, other):
        self.bottom = min(self.bottom, other.bottom)
        self.left = min(self.left, other.left)
        self.top = max(self.top, other.top)
        self.right = max(self.right, other.right)


class Scanner:
    def __init__(self, name, position=Point(0, 0)):
        self.name = name
        # This is our position relative to scanner 0.
        self.position = position
        self.beacons = []

    def __repr__(self):
        return f"Scanner(name={self.name}, position={self.position}, beacons={self.beacons})"

    def add_beacon(self, beacon):
        self.beacons.append(beacon)

    def get_beacon_array(self):
        # Return our beacons as an n x 2 array, one row per beacon.
        return np.array([[b.x, b.y] for b in self.beacons])

    def set_position(self, position):
        # Set our position relative to scanner 0, thus mapping our beacons
        # into the same shared space.
        self.position = position

        # Update our beacon positions.
        self.beacons = [b + position for b in self.beacons]


class Grid:
    def __init__(self, bounds):
        self.grid = np.full(
            shape=(
                bounds.top - bounds.bottom + 1,
                bounds.right - bounds.left + 1,
            ),
            fill_value=".",
            dtype=np.str_,
        )
        self.bounds = bounds

    def set_cell(self, p, c):
        x = p.x - self.bounds.left
        y = p.y - self.bounds.bottom
        self.grid[y][x] = c

    def print(self):
        for y in range(self.grid.shape[0] - 1, -1, -1):
            for x in range(0, self.grid.shape[1]):
                print(self.grid[y][x], end='')
            print()
        print()


def draw_map(scanners):
    # Get the bounds for the entire map.
    bounds = Bounds.empty()
    for s in scanners:
        bounds.extend(s.position)
        bounds.union(Bounds.get_bounds(s.beacons))

    grid = Grid(bounds)
    for s in scanners:
        # todo: don't assume all scanners are at (0, 0)
        grid.set_cell(s.position, "S")
        for b in s.beacons:
            grid.set_cell(b, "B")

    grid.print()


def parse_reports(reports):
    scanner = None
    scanners = []
    for line in reports:
        line = line.strip()
        if not line:
            # Empty line.
            continue
        elif m := re.match("--- scanner (\d+) ---", line):
            # This line starts a new scanner.
            scanner = Scanner(name=m[1])
            scanners.append(scanner)
            print(f"Found scanner: {scanner.name}.")
        else:
            # This line must be a beacon position.
            x, y = [int(x) for x in line.split(",")]
            scanner.add_beacon(Point(x, y))
            print(f"Found beacon at position ({x}, {y}) relative to scanner {scanner.name}.")
    return scanners


def build_distance_matrix(scanner):
    A = scanner.get_beacon_array()
    a = A.reshape((-1, 1, 2))
    b = A.reshape((1, -1, 2))
    return np.linalg.norm(a - b, axis=2)


def refine_constraints(constraints, bid, matches):
    print(f"Refining constraints for beacon {bid}.")
    c = constraints[bid]
    print(f"Starting constraints: {c}, new matches: {matches}.")
    c &= matches
    print(f"Updated constraints: {c}")
    constraints[bid] = c


# Given two scanners, return a map from the beacon IDs of the first scanner
# to the matching IDs of the second scanner.
def match_beacons(s0, s1):
    # Build a dictionary from dist -> [(beacon_1, beacon_2), ...] for the first
    # scanner.
    #
    # To get all the distances, we're going to reshape the array of points to an
    # (n, 1, 2) array, then subtract the "transpose" of the array from itself,
    # and let broadcasting handle the rest. Note this isn't really the transpose
    # since that would be a (2, 1, n) array, but we need a (1, n, 2) array for
    # broadcasting.
    print("Computing distance matrix for scanner 0.")
    distance_matrix = build_distance_matrix(s0)
    distance_map = defaultdict(list)
    for (i, j), d in np.ndenumerate(distance_matrix):
        # We only need the upper diagonal.
        if j > i:
            distance_map[d].append((i, j))

    # Now we can build the distance matrix for the second scanner, and for each
    # pair, we can quickly check to see if we have a matching distance in the
    # first scanner's output. If we find a pair with the same distance, then we
    # have a (potential) match for the two beacons. We can fix that match, then
    # keep going and try to match the remaining beacons.
    print("Computing distance matrix for scanner 1.")
    tmp = build_distance_matrix(s1)

    print("Checking for matching distances.")
    constraints = defaultdict(lambda: set(range(3)))
    for (i, j), d in np.ndenumerate(tmp):
        # We only need to check the upper diagonal.
        if j > i:
            print(f"Checking beacons {i}, {j}.")
            # Do we have a matching distance?
            if d in distance_map:
                print(f"Found match for distance {d:0.05f}: {distance_map[d]}")

                # TODO: handle case where we have more than one match for a distance
                matches = distance_map[d]
                if len(matches) > 1:
                    raise ValueError("Too many matches for distance: {d}!")

                # Refine our constraints for this beacon.
                refine_constraints(constraints, i, set(matches[0]))
                refine_constraints(constraints, j, set(matches[0]))

    print(f"Got constraints: {constraints}")

    # TODO: return list of matches, not a list of constraints?
    return constraints


def main():
    # In this problem, our goal is to build a map from a set of beacons and
    # scanners. The beacons and scanners do not move (i.e. their positions are
    # fixed), and each scanner is able to detect beacons up to 1000 units away
    # on any axis (x, y, or z; i.e., the detection volume is a cube of side
    # length 1000). The scanners are able to determine the precise position of
    # each beacon they can see, relative to the scanner. The scanners cannot
    # detect other scanners.
    #
    # The scanners do not know their own positions, but they are located in a
    # single contiguous 3d volume (i.e. there are no gaps in coverage between
    # scanners). We can reconstruct the volume by finding pairs of scanners with
    # overlapping detection volumes s.t. there are at least 12 beacons that both
    # scanners can detect within the overlap. By finding 12 common beacons, we
    # can precisely determine the positions of the scanners relative to each
    # other.
    #
    # TODO: Why do we need 12 matching beacons?
    #
    # Start with the most basic test case: two scanners that each see the same
    # three beacons.
    reports = """
--- scanner 0 ---
0,2
4,1
3,3

--- scanner 1 ---
-1,-1
-5,0
-2,1
"""

    # Parse the reports, and draw a map of which each scanner sees.
    scanners = parse_reports(reports.splitlines())
    for scanner in scanners:
        draw_map([scanner])

    # Match up the beacons seen by each scanner.
    #
    # TODO: don't assume there are only two scanners!
    constraints = match_beacons(scanners[0], scanners[1])

    print(constraints)
    print(list(constraints[0])[0])

    # Check that we found enough beacons in common between the two scanners.
    c = { k: v for k, v in constraints.items() if len(v) == 1 }

    if len(c) < 3:
        raise ValueError("Failed to find enough common beacons!")

    # Compute the offset between the scanners. To get the offset, we take the
    # first beacon from scanner 1, find its position as seen by scanner 0, and
    # then simply subtract the points -- this gives us the offset of scanner 1,
    # relative to scanner 0.
    b0 = scanners[1].beacons[0]
    b1 = scanners[0].beacons[list(constraints[0])[0]]
    offset = b1 - b0
    print(offset)
    scanners[1].set_position(offset)

    # Print the combined map for the two scanners.
    draw_map(scanners)

if __name__ == "__main__":
    main()
