#!/usr/bin/env python3

import functools
import math

def fuel_required(m):
    return math.floor(m / 3.0) - 2

def solve(input):
    total = 0
    for m in input:
        fuel_for_component = fuel_required(m)
        total += fuel_for_component
        print(f"fuel_required({m:07}) = {fuel_for_component}, new total is {total:07}.")
    return total

def solve2(input):
    # This originally didn't work since I left out the initializer!
    return functools.reduce(lambda t, x: t + fuel_required(x), input, 0)

if __name__=="__main__":
    # For a mass of 12, divide by 3 and round down to get 4, then subtract 2 to get 2.
    # For a mass of 14, dividing by 3 and rounding down still yields 4, so the fuel required is also 2.
    # For a mass of 1969, the fuel required is 654.
    # For a mass of 100756, the fuel required is 33583.
    for m, f in [(12, 2), (14, 2), (1969, 654), (100756, 33583)]:
        print(f"fuel_required({m}) = {fuel_required(m)} (expected {f}).")
    print("-----------")

    with open("input", "r") as f:
        output = solve2((int(l) for l in f))
        print(f"The answer is {output}.")
