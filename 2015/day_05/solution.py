#!/usr/bin/env python3

import unittest

def is_nice(s):
    # Nice strings:
    #
    #   1. Contain at least 3 vowels (aeiou).
    #
    #   2. Contain at least one letter that appears twice in a row (e.g. "aa")
    #
    #   3. Do not contain the strings ab, cd, pq, or xy, even if they are part
    #      of one of the other requirements.
    #
    # Note that the letters used by the rules may overlap; e.g. "aaa" is a nice
    # string, since it has three vowels and a letter that appears twice in a
    # row.
    #
    # I'm pretty sure we could do this with an NFA...
    vowel_count = 0
    has_double = False
    last_letter = None
    for i in range(len(s)):
        c = s[i]
        if c in "aeiou":
            vowel_count += 1
        if last_letter:
            if c == last_letter:
                has_double = True
            x = last_letter + c
            if x in set(["ab", "cd", "pq", "xy"]):
                # print(f"Found banned substring: {x}!")
                return False # naughty!
        last_letter = c
    return vowel_count >= 3 and has_double

def test_is_nice():
    print(f"is_nice(\"ugknbfddgicrmopn\") = {is_nice('ugknbfddgicrmopn')}")
    print(f"is_nice(\"aaa\")              = {is_nice('aaa')}")
    print(f"is_nice(\"jchzalrnumimnmhp\") = {is_nice('jchzalrnumimnmhp')}")
    print(f"is_nice(\"haegwjzuvuyypxyu\") = {is_nice('haegwjzuvuyypxyu')}")
    print(f"is_nice(\"dvszwmarrgswjxmb\") = {is_nice('dvszwmarrgswjxmb')}")

def is_nicer(s):
    # In part 2, nice strings:
    #
    #  1. contain a pair of letters that appears at least twice, without
    #     overlapping (e.g. "xyxy" works but "aaa" doesn't)
    #
    #  2. contain at least one letter which repeats with exactly one letter in
    #     between (e.g. "xyx", but note that "aaa" is also valid)
    #
    # Pairs of letters we've seen already, and their start index. Note that
    # we only need the start index from the first time we encounter the pair.
    print(f"Checking {s}")
    pairs = {}
    found_pair = False
    found_repeat = False
    for i in range(1, len(s)):
        # The bounds here look wrong, but remember that slices are exclusive of
        # the upper end.
        new_pair = s[i-1:i+1]
        if new_pair in pairs:
            # For the pair to not overlap with this one, it has to start at least
            # three characters back from our current position:
            #
            #  0 1 2 3
            #  -------
            #  a b a b
            #        ^
            if pairs[new_pair] < i - 2:
                print(f"Found non-overlapping repeated pair {new_pair} at {pairs[new_pair]}, {i - 1}.")
                found_pair = True
        else:
            pairs[new_pair] = i - 1

        if i > 1 and not found_repeat:
            found_repeat = s[i - 2] == s[i]
            if found_repeat:
                print(f"Found repeat {s[i-2:i+1]} at {i - 2}.")

        if found_pair and found_repeat:
            print(f"{s} is nice")
            return True
    print(f"{s} is naughty")
    return False

class TestIsNice(unittest.TestCase):
    def test_is_nicer(self):
        self.assertTrue(is_nicer("qjhvhtzxzqqjkmpb"))
        self.assertTrue(is_nicer("xxyxx"))
        self.assertFalse(is_nicer("uurcxstgmygtbstg"))
        self.assertFalse(is_nicer("ieodomkazucvgmuy"))

def count_if(iterable, fn):
    return sum([1 for x in iterable if fn(x)])
    
def main():
    def count_nice_strings(fn):
        with open("input.txt") as input_file:
            return count_if([x.strip() for x in input_file], fn)

    nice_count = count_nice_strings(is_nice)
    print(f"Got {nice_count} nice strings in part 1.")

    nice_count = count_nice_strings(is_nicer)
    print(f"Got {nice_count} even nicer strings in part 2.")

if __name__ == "__main__":
    main()
