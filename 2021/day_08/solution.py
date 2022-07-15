#!/usr/bin/env python3
#
# For part 1, we just need to count how often the digits 1, 4, 7, and 8 appear
# in the output values of our input data. Since each of these digits uses a
# unique number of segments (2, 4, 3, and 7, respectively), it should be easy
# count how often they appear.

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()

    digit_count = 0
    for line in args.input_file:
        # print(line)
        tokens = line.split()
        # print(tokens)

        # For part 1, we can ignore everything before the '|'.
        i = 0
        while i < len(tokens):
            # print(tokens[i])
            if tokens[i] == "|":
                break
            i += 1
            
        # Now we just count the occurrences of the digits 1, 4, 7, or 8 in the
        # output.
        i += 1  # skip '|'
        while i < len(tokens):
            c = len(tokens[i])
            if c == 2 or c == 3 or c == 4 or c == 7:
                digit_count += 1
            i += 1

    print(f"Found {digit_count} 1, 4, 7, or 8 digits in the input.")

if __name__ == "__main__":
    main()
