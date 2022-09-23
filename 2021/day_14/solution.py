#!/usr/bin/env python3

import argparse
import copy
import itertools
import re

from collections import Counter

def truncate(s, max_width=80):
    if len(s) < max_width:
        return s
    return s[0:max_width] + "..."

def make_pairs(s):
    return [''.join(p) for p in itertools.pairwise(s)]

def check_pair_counts(counts, expected):
    keys = counts.keys() | expected.keys()
    for k in sorted(keys):
        if counts[k] != expected[k]:
            print(f"CHECK: Counts don't match for {k}!")
                    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--max_time_step", type=int, default=10)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--update-template", action="store_true")
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
        m = re.match("(\w\w) -> (\w)", line)
        if not m:
            raise ValueError(f"Invalid syntax: {line}")
        rules[m[1]] = m[2]

    print(f"Got rules: ")
    for r in rules:
        print(f"  {r} -> {rules[r]}")

    # Apply rules to the template, and keep track of the count of each
    # character.
    #
    # Storing the actual template in memory isn't fast enough for part 2, which
    # asks us to run 40 iterations. Instead, we can just store counts of pairs.
    # Each rule transforms one pair into two new pairs (by inserting a new
    # character between two existing characters). As long as we know how many of
    # each pair are in the template, their exact positions don't matter. Note
    # that the pair counts count some characters multiple times (since all
    # characters except for the first an the last one occur in exactly two
    # pairs).
    pair_counts = Counter(make_pairs(template))
    letter_counts = Counter(template)
    for t in range(1, args.max_time_step + 1):
        if not args.update_template:
            print(f"Running timestep: {t}")
        if args.verbose:          
            print(f"  Starting pair counts: {pair_counts}")
            if args.update_template:
                print(f"  Starting template: {template}")

        if args.update_template:
            # Track the template too so we can see if it lines up. This will only
            # work for a small number of timesteps!
            new_template = ''
            for p in make_pairs(template):
                c = rules[p]
                new_template += p[0] + c
            new_template += template[-1]
            template = new_template

        # We can't mutate our pair counts while iterating over them, so we keep
        # a set of deltas to apply after we're done.
        updates = Counter()
        for p in pair_counts.keys():
            # Ignore pairs which have a count of 0; they're not in the template
            # any more.
            count = pair_counts[p]
            assert count >= 0
            if count == 0:
                continue
            
            c = rules[p]

            if args.verbose:
                print(f"    {p} -> {p[0] + c + p[1]}")

            updates[p] -= count
            updates[p[0] + c] += count
            updates[c + p[1]] += count
            letter_counts[c] += count

        pair_counts = pair_counts + updates
        if args.verbose:
            print(f"  Got updates: {updates}")
            print(f"  Updated pair counts: {pair_counts}")

        if args.update_template:
            # Check that pairs matches template -- only works if we actually track
            # the template string in memory!
            expected_pair_counts = Counter(make_pairs(template))
            if args.verbose:
                print(f"  Expected pair counts: {expected_pair_counts}")
            check_pair_counts(pair_counts, expected_pair_counts)
            print(f"After step {t:3}: {truncate(template, 61)}")
            
    print(f"Counts after step {t}: {letter_counts}")
    mc = letter_counts.most_common()[0]
    lc = letter_counts.most_common()[-1]
    print(f"Most common letter: {mc[0]}")
    print(f"Least common letter: {lc[0]}")
    print(f"Difference: {mc[1] - lc[1]}")

if __name__ == "__main__":
    main()
