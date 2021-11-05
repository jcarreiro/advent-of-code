import math
import numpy as np
import time

from collections import defaultdict, namedtuple
from typing import List

Point = namedtuple("Point", ["x", "y"])
Vector = namedtuple("Vector", ["x", "y"])
Polar = namedtuple("Polar", ["r", "theta"])

def point_to_polar(p: Point) -> Polar:
    return Polar(r=math.sqrt(p.x**2 + p.y**2), theta=math.atan2(p.y, p.x))

def polar_to_point(p: Polar) -> Point:
    return Point(x=p.r * math.cos(p.theta), y=p.r * math.sin(p.theta))

def parse_map(lines):
    asteroids = []
    y = 0
    for line in lines:
        line = line.rstrip()
        print(f"Got line: {line}")
        x = 0
        for c in line:
            if c == '#':
                print(f"Found asteroid at {(x, y)}")
                asteroids.append(Point(x, y))
            x += 1
        y += 1
    print(f"Finished parsing map, x={x}, y={y}")
    return asteroids, Point(x, y)

def read_map(path):
    with open(path) as f:
        return parse_map(f)

def distance(p0, p1):
    dx = p0.x - p1.x
    dy = p0.y - p1.y
    return math.sqrt(dx**2 + dy**2)

can_see_cache = {}

# TODO: memoize this (the relation is symmetric)
def can_see(asteroids, a0, a1):
    assert(a0 != a1)

    # Have we already checked this pair?
    if (a0, a1) in can_see_cache:
        return can_see_cache[(a0, a1)]
    elif (a1, a0) in can_see_cache:
        return can_see_cache[(a1, a0)]

    # We can see a1 unless another asteroid lies exactly on the line (a0, a1),
    # and is between a0 and a1:
    #
    #   --a0-----a2--------a1--
    #
    # In this case, dist(a0, a2) + dist(a2, a1) = dist(a0, a1). In any other
    # case, the distances will not be equal. Consider:
    #
    #   --a2-----a0--------a1--
    #
    # Then dist(a0, a2) + dist(a2, a1) > dist(a0, a1). The case where a2 is on
    # the line segment (a1,...) is symmetric. Finally, if a2 is not colinear
    # with a0, a1, then dist(a0, a2) + dist(a2, a1) != dist(a0, a1) by the
    # triangle inequality.
    ret = True
    for a2 in asteroids:
        if a0 == a2 or a1 == a2:
            continue
        # print(f"    Considering {a2}")
        d01 = distance(a0, a1)
        d02 = distance(a0, a2)
        d12 = distance(a1, a2)
        # print(f"    d01 = {d01}, d02 = {d02}, d12 = {d12}")
        # Note that comparing for equality here doesn't work for obvious
        # reasons. Instead we do the typical thing for floating point and
        # look for approximate equality.
        epsilon = 1e-6
        if distance(a0, a2) + distance(a2, a1) - distance(a0, a1) < epsilon:
            # print(f"    {a0} can't see {a1}, blocked by {a2}.")
            ret = False
            break

    # Update cache
    can_see_cache[(a0, a1)] = ret
    return ret

# Get the number of other asteroids visible from the given asteroid. This is the
# slow (O(n^3)) version (it uses can_see, which considers all other asteroids
# for each pair (a0, a1)).
def count_visible_slow(asteroids, a0):
    count = 0
    for a1 in asteroids:
        if a0 == a1:
            # Don't check asteroids against themselves.
            continue
        elif can_see(asteroids, a0, a1):
            count += 1
    return count

# This version converts to polar coordinates, relative to the origin a0. After
# converting to polar coordinates, we simply need to bucket asteroids by theta.
# Only one asteroid from each bucket can be seen. Note that there is no need to
# even sort the buckets since it doesn't matter which of the asteroids we can
# see if all we want to do is get a count of the asteroids which are visible.
def count_visible_fast(asteroids, a0, epsilon=0.001):
    # Transform asteroids to new origin.
    asteroids = [Point(x=a.x - a0.x, y=a.y - a0.y) for a in asteroids]

    # Convert to polar coordinates.
    asteroids = [point_to_polar(a) for a in asteroids]

    # Bucket asteroids (use epsilon to round).
    assert(epsilon < 1)
    ndigits = -math.log10(epsilon)
    d = defaultdict(list)
    for a in asteroids:
        d[round(a.theta, int(ndigits))].append(a)

    # Return count of buckets (easy!).
    return len(d)

# This version does no work. The result is not correct (for obvious reasons) but
# it's useful for benchmarking since it's the fastest possible "solution".
def count_visible_zero(asteroids, a0):
    return 0

# TODO: this would be faster if we used the same trick from part 2 below
# (convert to polar coordinates) -- it'd be O(n^2) instead of O(n^3) (for
# each asteroid, convert all other asteroids to polar using that asteroid
# as origin; keep closest asteroid for each angle; count them). Note that
# since we memoized the can_see method the speedup might not be that big
# in practice.
def solve_part1(asteroids: List[Point], count_visible_fn=count_visible_slow) -> Point:
    # In this problem, we are given a (2d) grid, each cell of which may be empty
    # ('.') or which may contain an asteroid ('#'). We need to find the asteroid
    # from which we can see the most other asteroids (asteroids block line of
    # sight to any asteroid behind them).
    #
    # The obvious way to do this is to consider, for each asteroid, all the
    # other asteroids in the grid, counting each as visible if no third asteroid
    # lies between it and the start point. This is not terribly efficient, but
    # it's a good place to start from since it is obviously correct.
    best_asteroid = None
    max_seen = 0
    i = 0
    total = len(asteroids)
    t0 = time.perf_counter()
    for a0 in asteroids:
        # print(f"Checking asteroid {a0}")
        i += 1
        if i % 10 == 0:
            elapsed = time.perf_counter() - t0
            pct_done = float(i) / float(total)
            a_per_s = float(i) / float(elapsed)
            eta = float(total - i) / a_per_s
            print(f"{i} / {total} asteroids checked ({pct_done:0.2%}, {a_per_s:0.2f} asteroids / sec), elapsed time {elapsed:0.2f} s, eta {eta:0.2f} s.")

        count = count_visible_fn(asteroids, a0)
        # print(f"Asteroid at position {a0.x, a0.y} can see {count} other asteroids.")

        if count > max_seen:
            best_asteroid = a0
            max_seen = count

    elapsed = time.perf_counter() - t0
    a_per_s = float(i) / float(elapsed)
    print(f"Checked {i} asteroids in {elapsed:0.2f} s ({a_per_s:0.2f} asteroids / s).")
    print(f"Best asteroid is {best_asteroid.x, best_asteroid.y} with {max_seen} other asteroids visible.")
    return best_asteroid

def draw_vaporized_map(vaporized, origin, rows, cols):
    grid = [['.' for j in range(cols)] for i in range(rows)]
    i = 1
    for v in vaporized[0:9]:
        grid[v.y][v.x] = str(i)
        i += 1

    for v in vaporized[9:]:
        grid[v.y][v.x] = '#'

    grid[origin.y][origin.x] = 'X'

    for r in grid:
        print(''.join(r))
    print()

# Asteroids is the parsed asteroid map. Origin is the location of the monitoring
# station. This method will remove the asteroid at the origin, if needed. Bounds
# are the bounds to use when printing the maps showing the order in which the
# asteroids are destroyed.
def solve_part2(asteroids, origin, bounds):
    # In part 2, the elves use a giant laser to vaporize the asteroids. The
    # laser starts at an angle of 0 deg from the vertical (i.e. pointing up) and
    # sweeps clockwise, vaporizing any asteroids it hits. We need to compute the
    # order in which the asteroids will be vaporized. To do that, we tranform
    # to radial coordinates and sort by distance. Easy.
    #
    # Angles that differ by less than this value are considered equal (ie. the
    # associated asteroids are considered to be on the same line from the
    # origin).
    epsilon = 0.001

    def transform(a: Point):
        # translate to new origin
        x = a.x - origin.x
        y = a.y - origin.y

        # rotate 90 deg CW
        new_x = y
        new_y = -x
        x = new_x
        y = new_y

        # convert to polar coords
        r = math.sqrt(x**2 + y**2)
        theta = math.atan2(y, x)
        return Polar(r, theta)

    def untransform(a: Polar):
        # convert to cart coords
        x = a.r * math.cos(a.theta)
        y = a.r * math.sin(a.theta)

        # rotate 90 CCW
        new_x = -y
        new_y = x
        x = new_x
        y = new_y

        # translate to orginal origin
        x += origin.x
        y += origin.y
        return Point(x, y)

    # Remove asteroid at origin if needed -- this is the location of the
    # monitoring station.
    asteroids = filter(lambda a: a.x != origin.x or a.y != origin.y, asteroids)

    # Transform to polar coordinates and rotate entire coordinate system by 90
    # deg CW (see note below).
    asteroids = [transform(a) for a in asteroids]

    # Turn epsilon into a number of digits (after decimal) to keep.
    assert(epsilon < 1)
    ndigits = int(-math.log10(epsilon))

    # Bucket asteroids by angle, then sort all buckets by distance.
    d = defaultdict(list)
    for a in asteroids:
        d[round(a.theta, ndigits)].append(a)

    for k in d.keys():
        d[k].sort(key=lambda a: a.r)

    # for k, v in sorted(d.items()):
    #     print(f"{k:0.03f}: {v}")

    # Ok. Now this part is a bit weird, but: our laser starts out pointing "up",
    # but this actually the -y direction (since in the given examples, +y points
    # down the page, according to the coordinates assigned to the asteroids).
    # The laser then rotates "clockwise", but, again, due to the fact that the
    # y-axis is swapped, the actual sense of the rotation is counterclockwise
    # (we are pointing "up" along the -y axis, and we rotate _toward_ the +x
    # axis -- this is counterclockwise).
    #
    # We rotated everything 90 deg clockwise earlier so that what was originally
    # the -y direction is now our -x, and what was originally our +x is now our
    # -y. So we can simply iterate from -pi to pi and we'll hit the buckets in
    # the same order as described in the problem statement.
    vaporized = []
    while len(vaporized) < len(asteroids):
        # Still asteroids left. Take the first asteroid from each non-empty
        # bucket.
        #
        # This is to handle the weird edge case where stuff on the (original) -y
        # axis ends up with a theta of either pi or -pi, but we want to make
        # sure it's "hit" first since the laser starts out pointing in that
        # direction.
        pi_rounded = round(math.pi, ndigits)
        if d[pi_rounded]:
            vaporized.append(d[pi_rounded].pop(0))
        for k, v in sorted(d.items()):
            if k < 3.142:
                # print(f"Checking bucket {k}")
                if v:
                    vaporized.append(v.pop(0))

    # Convert back to the original coordinate system. Because of numerical error
    # we end up with coordinates that aren't quite integers; we just round to
    # the nearest integer to fix this.
    vaporized = [untransform(a) for a in vaporized]
    vaporized = [Point(x=round(v.x), y=round(v.y)) for v in vaporized]

    # Print out the order the asteroids were vaporized, and some nice maps, just
    # like in the problem statement.
    print(f"Asteroids were vaporized in this order:")

    def get_suffix(i):
        if i == 1:
            return "st"
        elif i == 2:
            return "nd"
        elif i == 3:
            return "rd"
        else:
            return "th"

    for i, v in enumerate(vaporized):
        suffix = get_suffix(i+1)
        if i == len(vaporized) - 1:
            suffix += " and final"
        print(f"The {i+1}{suffix} asteroid to be vaporized is at {v.x,v.y}.")

    rows = bounds.y
    cols = bounds.x
    while vaporized:
        draw_vaporized_map(vaporized, origin, rows, cols)
        vaporized = vaporized[9:]

if __name__ == "__main__":
    asteroids, bounds = read_map("input")

    # Solve part one to get location of monitoring station.
    # origin = solve_part1(asteroids, count_visible_fast)

    # Now solve part 2.
    solve_part2(asteroids, origin=Point(x=11, y=19), bounds=bounds)
