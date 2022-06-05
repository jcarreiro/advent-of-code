#!/usr/bin/env python3

from collections import deque

def parse_ages(line):
    ages = [0] * 9
    for age in line.split(","):
        ages[int(age)] += 1
    return ages
        
def simulate(ages, max_timestep):
    print(f"Got starting ages: {ages}.")
    fish = deque(ages)
    for t in range(max_timestep):
        print(f"Day {t+1}: {','.join([str(x) for x in fish])}")
        b = fish.popleft()
        fish[6] += b
        fish.append(b)
    print(f"Total fish after {t+1} days: {sum(fish)}")

def main():
    # In this puzzle, we hvae a list of the ages (in days) of a group of
    # lanternfish. Each lanternfish produces a new lanternfish every 7 days; a
    # new lanternfish produces its first offspring after 9 days, after which it
    # produces additional offspring every 7 days as usual. The goal is to take
    # as input a list of ages, simulate their reproduction, and then produce
    # the total number of laternfish after a given number of days as output.
    test_input = "3,4,3,1,2"

    with open("input.txt") as infile:
        line = infile.readline()

    ages = parse_ages(line)
    simulate(ages, max_timestep=256)
        
if __name__ == "__main__":
    main()
