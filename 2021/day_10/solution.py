#!/usr/bin/env python3

import argparse
import functools
import numpy as np

# The opening brace we expect for each kind of closing brace.
MATCH = {
    # Forward matches.
    "[": "]",
    "(": ")",
    "{": "}",
    "<": ">",

    # Backward matches.
    "]": "[",
    ")": "(",
    "}": "{",
    ">": "<",
}

# Parse a line, returning the stack of open braces and the first mismatched
# input character, if any.
def parse_line(line):
    s = []  # our stack
    for c in line:
        if c in "[({<":
            # Open bracket => push on stack.
            s.append(c)
        elif c in "])}>":
            # Closing bracket => check top of stack for match.
            if s[-1] != MATCH[c]:
                # Stop at the first mismatched character.
                return (s, c)
            else:
                # Matching brace, remove opening brace for set from stack.
                s.pop(-1)

    # If we get here, the line didn't have any mismatched braces.
    return (s, None)

# For part 1, we are given a series of lines, each of which is composed of
# opening and closing braces of various kinds ("[", "(", "{", "<", and the
# closing brace for each). We need to detect the first mismatched closing
# brace on each line (if there is one). This is easily done with a stack.
def solve_part1(input_file):
    mismatches = []
    for line in input_file:
        _, c = parse_line(line.strip())
        if c:
            # Remember the mismatched characters we saw.
            mismatches.append(c)

    print(mismatches)

    # Now we can compute our score!
    POINTS = {
        ")": 3,
        "]": 57,
        "}": 1197,
        ">": 25137,
    }
    score = sum(map(lambda x: POINTS[x], mismatches))
    print(f"Got score: {score}")

# For part 2, we need to ignore the "corrupted" lines (lines with a mismatched
# closing brace) and figure out how to complete the remaining lines (ie., find
# the sequence of closing braces needed to correctly close any unclosed open
# braces. We use the same basic approach as in part 1.
def solve_part2(input_file):
    # Score for each line that has a valid completion.
    scores = []
    for line in input_file:
        s, c = parse_line(line.strip())
        if c:
            # This line is corrupted.
            continue

        # Map the (reversed) stack to the closing characters we need.
        completion_str = ''.join(map(lambda c: MATCH[c], reversed(s)))

        # Compute score for this completion. For each character in the
        # completion string, we first multiply the current score by 5,
        # then add the points for the character.
        POINTS = dict(zip(")]}>", range(1,5)))
        score = functools.reduce(lambda x, y: 5 * x + y, [POINTS[c] for c in completion_str], 0)
        scores.append(score)
        print(f"Got score: {score} for completion_str: {completion_str}.")

    # The answer is the median score.
    print(f"Median score is: {np.median(scores)}.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()
    solve_part2(args.input_file)

if __name__ == "__main__":
    main()
