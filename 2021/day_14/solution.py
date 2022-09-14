#!/usr/bin/env python3

import argparse
import itertools
import re

from collections import defaultdict

def truncate(s, max_width=80):
    if len(s) < max_width:
        return s
    return s[0:max_width] + "..."

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--max_time_step", type=int, default=10)
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()

    # The first line should be the template.
    template = args.input_file.readline().strip()
    print(f"Got template: {template}")

    # Skip the blank line.
    args.input_file.readline()

    # The rest of the lines should be the substitution rules.
    rules = {}
    for line in args.input_file:
        line = line.strip()

        # print(line)

        m = re.match("(\w\w) -> (\w)", line)
        if not m:
            raise ValueError(f"Invalid syntax: {line}")
        print(f"{m[1]} -> {m[2]}")
        rules[m[1]] = m[2]

    print(f"Got rules: {rules}")

    # Apply rules to the template, and keep track of the count of each
    # character.
    counts = defaultdict(int)
    for c in template:
        counts[c] += 1

    print(f"Template: {template}")
    for t in range(1, args.max_time_step + 1):
        next_template = ''
        for p in itertools.pairwise(template):
            # Apply rule and update count.
            c = rules[''.join(p)]
            next_template += p[0]
            next_template += c
            counts[c] += 1
            
        # Swap template.
        template = next_template + template[-1]
        print(f"After step {t:03}: {truncate(template, 60)}")

    print(f"Counts after step {t}: {counts}")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1])
    print(f"Most common letter: {sorted_counts[-1]}")
    print(f"Least common letter: {sorted_counts[0]}")
    print(f"Difference: {sorted_counts[-1][1] - sorted_counts[0][1]}")

if __name__ == "__main__":
    main()
