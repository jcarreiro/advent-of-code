import math
import numpy as np
import time

from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
Vector = namedtuple("Vector", ["x", "y"])

def read_map(path):
    with open(path) as f:
        asteroids = []
        y = 0
        for line in f:
            print(f"Got line: {line}")
            x = 0
            for c in line:
                if c == '#':
                    print(f"Found asteroid at {(x, y)}")
                    asteroids.append(Point(x, y))
                x += 1
            y += 1
        return asteroids

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


if __name__ == "__main__":
    # In this problem, we are given a (2d) grid, each cell of which may be empty
    # ('.') or which may contain an asteroid ('#'). We need to find the asteroid
    # from which we can see the most other asteroids (asteroids block line of
    # sight to any asteroid behind them).
    #
    # The obvious way to do this is to consider, for each asteroid, all the
    # other asteroids in the grid, counting each as visible if no third asteroid
    # lies between it and the start point. This is not terribly efficient, but
    # it's a good place to start from since it is obviously correct.
    asteroids = read_map("input")
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


        # Count how many asteroids this asteroid can see.
        count = 0
        for a1 in asteroids:
            if a0 == a1:
                continue
            # print(f"  Considering asteroid {a1}")
            if can_see(asteroids, a0, a1):
                # print(f"  {a0} can see {a1}!")
                count += 1

        # print(f"Asteroid at position {a0.x, a0.y} can see {count} other asteroids.")

        if count > max_seen:
            best_asteroid = a0
            max_seen = count

    elapsed = time.perf_counter() - t0
    a_per_s = float(i) / float(elapsed)
    print(f"Checked {i} asteroids in {elapsed:0.2f} s ({a_per_s:0.2f} asteroids / s).")
    print(f"Best asteroid is {best_asteroid.x, best_asteroid.y} with {max_seen} other asteroids visible.")
