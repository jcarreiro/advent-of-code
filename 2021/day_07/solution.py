#!/usr/bin/env python3

import argparse
import numpy as np

# In this problem, we're given a list of positions along a line. The positions
# are the starting positions of a bunch of "crabs", and we want to get them all
# to line up on the same spot. Moving along the line uses "fuel", and we want to
# choose the target point so as to minimize the total fuel used.
def solve_part1(positions):
    # In part 1, the cost of moving is simply the distance between the crab and
    # the target point, so the best target is simply the median of the input
    # positions.
    x = int(np.median(positions))
    cost = np.sum(np.abs(positions - x))
    return (x, cost)


def part2_cost(x, positions):
    D = np.abs(positions - x)
    return np.sum(D * (D + 1) / 2.)

def solve_part2(positions):
    # In part 2, the cost of moving increases per unit of distance moved (1 fuel
    # for 1 unit of distance, 3 for 2, 6 for 3, etc; note that these are exactly
    # the triangular numbers). In this case, it's more effective to reduce the
    # distance that the crabs furthest away from the target point need to move,
    # since they represent the largest cost.
    #
    # The cost is this case is f(x) = x(x - 1) / 2, where x is the distance from
    # the crab's starting position to the target point.
    mean = np.mean(positions)
    print(f"Got mean: {mean}")

    # If the mean isn't a whole number, check floor() and ceil(), since either
    # one of them could be the optimal point.
    #
    # XXX I don't understand why round() doesn't work -- how we can get a mean
    #     with fractional part > 1/2 and still have floor() be the optimal
    #     point?
    lo = np.floor(mean)
    lo_cost = part2_cost(lo, positions)
    print(f"Got floor {lo}, floor cost {lo_cost}.")

    hi = np.ceil(mean)
    hi_cost = part2_cost(hi, positions)
    print(f"Got ceil  {hi}, ceil  cost {hi_cost}.")

    if lo_cost > hi_cost:
        return (hi, hi_cost)
    else:
        return (lo, lo_cost)

# Mean doesn't seem to work, let's exhaustively check all options, then once
# we have the correct answer we can try to optimize.
def solve_part2_slow(positions):
    best_x = None
    best_cost = None
    for x in np.arange(np.min(positions), np.max(positions) + 1):
        D = np.abs(positions - x)
        c = np.sum(D * (D + 1) / 2)
        print(f">>> Got cost {c} for x = {x}.")
        if not best_cost or c < best_cost:
            print(f"!!! New best cost is {c}, best x is {x}.")
            best_x = x
            best_cost = c
    return (best_x, best_cost)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()
    positions = np.array([int(x) for x in args.input_file.readline().strip().split(",")])
    print(f"Got positions: {positions}")

    x, cost = solve_part1(positions)
    print(f"For part 1, best position is {x}, with cost {cost}.")

    x, cost = solve_part2(positions)
    print(f"For part 2, best position is {x}, with cost {cost}.")

    
if __name__ == "__main__":
    main()
