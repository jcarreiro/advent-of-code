#!/usr/bin/env python3

import argparse

from collections import defaultdict

# For part 1, we just need to count how often the digits 1, 4, 7, and 8 appear
# in the output values of our input data. Since each of these digits uses a
# unique number of segments (2, 4, 3, and 7, respectively), it should be easy
# count how often they appear.
def solve_part1(input_file):
    digit_count = 0
    for line in input_file:
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


# For part 2, we need to find the actual output for each input line, then sum up
# all the outputs. For reference, the segments on the display are named like
# this:
#
#     aaaa
#    b    c
#    b    c
#     dddd
#    e    f
#    e    f
#     gggg
#
# Diff two signal patterns and return the set of wires that are different.
#
# Params
# ------
# digits: map from digit (1) to pattern for digit ('cf').
# a: digit or pattern to diff
# b: digit or pattern to diff
def diff(digits, a, b):
    if isinstance(a, int):
        a = digits[a]
    if isinstance(b, int):
        b = digits[b]
    return set(a) - set(b)

# Diff two signal patterns and return the single wire that is different.
#
# Params
# ------
# digits: map from digit (1) to pattern for digit ('cf').
# a: digit or pattern to diff
# b: digit or pattern to diff
def diff_one(digits, a, b):
    d = diff(digits, a, b)
    assert(len(d) == 1)
    return d.pop()

# Maps from segments to (scrambled) wire for segment, e.g. "cf" -> "ab".
def map_segments(segments, pattern):
    return "".join([segments[s] for s in pattern])

# Parse a line into the signal patterns and outputs to decode.
def parse_input_line(line):
    tokens = line.split()

    print(tokens)

    inputs_done = False
    signals = defaultdict(list)
    outputs = []
    i = 0
    while i < len(tokens):
        token = tokens[i]

        print(token)

        i += 1
        if token == "|":
            # No more inputs; the rest of the line is the output digits.
            assert(not inputs_done)
            inputs_done = True
        else:
            if not inputs_done:
                signals[len(token)].append(token)
            else:
                outputs.append(token)
    return (signals, outputs)

def strsort(s):
    return ''.join(sorted(s))

def decode_line(line):
    # We're going to need to go over the input signal patterns multiple
    # times. To make finding specific digits easier, let's put them in a
    # dictionary where the key is the pattern length.
    signals, outputs = parse_input_line(line)

    print(signals, outputs)

    # We should only have one signal of length 2, 3, 4, and 7 (see above).
    for x in [2, 3, 4, 7]:
        assert(len(signals[x]) == 1)

    # This table goes from the output digit (e.g. '1') to the signal pattern
    # for that digit (e.g. 'ab').
    digits = {
        1: signals[2][0],
        4: signals[4][0],
        7: signals[3][0],
        8: signals[7][0],
    }

    # Now we can use the different signal patterns to figure out which wire
    # is mapped to which segment. This is the map from signal wire to
    # segment.
    segments = {}

    # The difference between '7' and '1' is the top segment ('a').
    segments["a"] = diff_one(digits, 7, 1)

    # '9' - '4' leaves only segments 'a' and 'g' (the top and bottom). We
    # know 'a', so the other must be 'g'. Additionally there are only 3
    # digits which have 6 segments illuminated ('0', '6', and '9'), and of
    # those 3 only '9' will have 2 segments left illuminated after we
    # subtract '4', so that also tells us which pattern represents the digit
    # '9'.
    for s in signals[6]:
        d = diff(digits, s, 4)
        if len(d) == 2:
            digits[9] = s
            seg = d.pop()
            if seg == segments["a"]:
                seg = d.pop()
            segments["g"] = seg

    # Now '8' - '9' gives us segment 'e'.
    segments["e"] = diff_one(digits, 8, 9)

    # '2' - '4' leaves 3 segments illuminated, '3' - '4' leaves 2, and '5' -
    # '4' also leaves 2. So that tells us the pattern for '2'.
    for s in signals[5]:
        d = diff(digits, s, 4)
        if len(d) == 3:
            digits[2] = s

    # '3' - '2' leaves just the segment 'f', but '5' - '2' leaves 'b' and
    # 'f'. So now we know the patterns for '3' and '5' and the wire for 'f'.
    for s in signals[5]:
        if s == digits[2]:
            continue
        d = diff(digits, s, 2)
        if len(d) == 1:
            digits[3] = s
            segments["f"] = d.pop()

            # Knowing 'f' also gives us 'c' (since it's the only other segment
            # illuminated for '1').
            segments["c"] = diff_one(digits, 1, map_segments(segments, "f"))

            # Since we know 'a', 'c', 'f', and 'g', the only thing left in '3'
            # must be 'd'.
            segments["d"] = diff_one(digits, s, map_segments(segments, "acfg"))
        elif len(d) == 2:
            digits[5] = s

    # Now that we know '3' and '5', '5' - '3' gives us the last segment 'b'.
    segments["b"] = diff_one(digits, 5, 3)

    # We have all the segments, so we can easily fill in any missing digits now.
    DIGITS = {
        0: "abcefg",
        1: "cf",
        2: "acdeg",
        3: "acdfg",
        4: "bcdf",
        5: "abdfg",
        6: "abdefg",
        7: "acf",
        8: "abcdefg",
        9: "abcdfg",
    }
    for digit, pattern in DIGITS.items():
        if not digit in digits:
            digits[digit] = map_segments(segments, pattern)

    print(segments)
    print(digits)

    # Print a fancy mapping.
    print(f"  {segments.get('a', '-') * 4}  ")
    print(f" {segments.get('b', '-')}    {segments.get('c', '-')} ")
    print(f" {segments.get('b', '-')}    {segments.get('c', '-')} ")
    print(f"  {segments.get('d', '-') * 4}  ")
    print(f" {segments.get('e', '-')}    {segments.get('f', '-')} ")
    print(f" {segments.get('e', '-')}    {segments.get('f', '-')} ")
    print(f"  {segments.get('g', '-') * 4}  ")

    # Invert the digits map so we can lookup patterns to get the intended
    # output digit.
    patterns = {strsort(v): k for k, v in digits.items()}

    print(patterns)

    # Now that we know the mapping, we can decode this line's output.
    output = 0
    for token in outputs:
        token = strsort(token)

        print(token)

        # shift digits over to left
        output *= 10

        # add in new digit
        output += patterns[token]

    print(output)
    
    return output
        
def solve_part2(input_file):
    output = sum(map(decode_line, input_file))
    print(f"Got total: {output}")
            
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()
    solve_part2(args.input_file)

if __name__ == "__main__":
    main()
