#!/usr/bin/env python3

import argparse

# For part 1, we are given a series of lines, each of which is composed of
# opening and closing braces of various kinds ("[", "(", "{", "<", and the
# closing brace for each). We need to detect the first mismatched closing
# brace on each line (if there is one). This is easily done with a stack.
def solve_part1(input_file):
    mismatches = []
    for line in input_file:
        line = line.strip()
        print(line)
        s = []  # our stack
        for c in line:
            print(c)

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
            
            if c in "[({<":
                # Open bracket => push on stack.
                s.append(c)
            elif c in "])}>":
                # Closing bracket => check top of stack for match.
                if s[-1] != MATCH[c]:
                    print(f"Found mismatched brace! Expected {MATCH[s[-1]]} but got {c}.")

                    # Remember the mismatched character for this line.
                    mismatches.append(c)

                    # Stop at the first mismatched character.
                    break
                else:
                    # Matching brace, remove opening brace for set from stack.
                    s.pop(-1)
                    
    print(mismatches)

    # Now we can compute our score!
    SCORES = {
        ")": 3,
        "]": 57,
        "}": 1197,
        ">": 25137,
    }
    score = sum(map(lambda x: SCORES[x], mismatches))
    print(f"Got score: {score}")
                
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()
    solve_part1(args.input_file)

if __name__ == "__main__":
    main()
