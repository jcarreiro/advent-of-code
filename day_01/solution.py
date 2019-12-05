#!/usr/bin/env python3

import functools
import math

def fuel_required(m):
    return math.floor(m / 3.0) - 2

# This version takes into account that fuel has mass, too (see below).
def fuel_required_part2(m):
    df = fuel_required(m)
    if df <= 0:
        return 0
    return df + fuel_required_part2(df)

def solve(input):
    total = 0
    for m in input:
        fuel_for_component = fuel_required(m)
        total += fuel_for_component
        print(f"fuel_required({m:07}) = {fuel_for_component}, new total is {total:07}.")
    return total

# In part 1 we just need to compute the total fuel needed based on the mass of
# each module (see the file "input" for the masses).
def solve_part1(input):
    # This originally didn't work since I left out the initializer!
    return functools.reduce(lambda t, x: t + fuel_required(x), input, 0)

# In part 2 we need to take into account that fuel has mass too! We need to add
# more fuel to account of the mass of the fuel, and so on, until the amount of
# fuel we need to add is <= 0 for a module.
#
# Note that we can't just work from the total fuel computed in part 1 -- we'll
# overestimate the fuel needed in that case, since the problem asks for us to
# do this per-module!
def solve_part2(input):
    return functools.reduce(lambda t, x: t + fuel_required_part2(x), input, 0)

if __name__=="__main__":
    # For a mass of 12, divide by 3 and round down to get 4, then subtract 2 to get 2.
    # For a mass of 14, dividing by 3 and rounding down still yields 4, so the fuel required is also 2.
    # For a mass of 1969, the fuel required is 654.
    # For a mass of 100756, the fuel required is 33583.
    for m, f in [(12, 2), (14, 2), (1969, 654), (100756, 33583)]:
        print(f"fuel_required({m}) = {fuel_required(m)} (expected {f}).")
    print("-----------")

    with open("input", "r") as f:
        part1_answer = solve_part1((int(l) for l in f))
        print(f"The answer to part 1 is {part1_answer}.")

        f.seek(0)  # it'd be more efficient to compute both totals at once...
        part2_answer = solve_part2((int(l) for l in f))
        print(f"The answer to part 2 is {part2_answer}.")
