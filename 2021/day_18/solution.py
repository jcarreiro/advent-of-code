#!/usr/bin/env python3

import argparse
import itertools
import json
import logging
import math

class SnailNumber:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"SnailNumber({self.left!r}, {self.right!r})"

    def __str__(self):
        return f"[{self.left}, {self.right}]"

    def __add__(self, other):
        # To add a two SnailNumbers, we first make a new pair from the parts,
        # then we reduce() the number.
        #
        # For convenience, we define SnailNumber(None, None) as the identity
        # element, i.e. SnailNumber(a, b) + SnailNumber(None, None) =
        # SnailNumber(a, b).
        if self.is_identity():
            return other
        elif other.is_identity():
            return self
        else:
            return SnailNumber(self, other).reduce()

    def __eq__(self, other):
        if isinstance(other, SnailNumber):
            return self.left == other.left and self.right == other.right
        else:
            return False

    def is_identity(self):
        return self.left == None or self.right == None

    def identity():
        return SnailNumber(None, None)

    def magnitude(self):
        def visit(n):
            if not isinstance(n, SnailNumber):
                return n
            else:
                return 3 * visit(n.left) + 2 * visit(n.right)
        return visit(self)

    def reduce(self):
        # Repeatedly explode or split until neither action applies.
        a = self
        b = None
        while True:
            logging.debug(f"Reducing {a}.")

            # Try to explode.
            b = a.explode()
            if b != a:
                logging.debug(f"{a} exploded!")
                a = b
                continue

            # Try to split.
            b = a.split()
            if b != a:
                logging.debug(f"{a} split!")
                a = b
                continue

            # If we get here then neither the explode nor the split action
            # changed the number, so we're done with this reduce step.
            logging.debug(f"{a} unchanged after explode/split, reduce finished.")
            break

        return a

    def explode(self):
        def visit(n, depth, exploded):
            logging.debug(f"Visiting: {n}, depth={depth}, exploded={exploded}.")
            # If we reach a depth of 4, and we haven't already exploded, then
            # this pair "explodes".
            if depth == 4 and not exploded:
                # We should never have SnailNumbers nested more than 4 deep,
                # since they should have exploded in a prior reduction step,
                # so check that here.
                assert not isinstance(n.left, SnailNumber)
                assert not isinstance(n.right, SnailNumber)

                # This pair is replaced by a 0 in the number, and we return
                # the parts to be added to the numbers to our left and right,
                # respectively.
                rv = (0, [n.left, n.right])
                logging.debug(f"{n} exploded! Returning {rv}.")
                return rv
            else:
                if isinstance(n.left, SnailNumber):
                    [left, lp] = visit(n.left, depth + 1, exploded)
                else:
                    left = n.left
                    lp = []

                if isinstance(n.right, SnailNumber):
                    [right, rp] = visit(n.right, depth + 1, exploded or bool(lp))
                else:
                    right = n.right
                    rp = []

                def add_to_predecessor(node, value):
                    logging.debug(f"Adding {value} to {node}.")
                    if isinstance(node.right, SnailNumber):
                        add_to_predecessor(node.right, value)
                    else:
                        node.right += value

                def add_to_successor(node, value):
                    logging.debug(f"Adding {value} to {node}.")
                    if isinstance(node.left, SnailNumber):
                        add_to_successor(node.left, value)
                    else:
                        node.left += value

                parts = []
                if lp:
                    # Our left child exploded. We can add the right part
                    # of the pair to the left child of our right child,
                    # then we need to return the rest up to our parent.
                    logging.debug(f"Adding {lp[1]} to right child: {right}.")
                    if isinstance(right, SnailNumber):
                        add_to_successor(right, lp[1])
                    else:
                        right += lp[1]
                    parts = [lp[0], 0]
                elif rp:
                    # Our right child exploded. We can add the left part
                    # of the pair to the right child of our left child,
                    # then we need to return the rest up to our parent.
                    logging.debug(f"Adding {rp[0]} to left child: {left}.")
                    if rp[0] != 0:
                        if isinstance(n.left, SnailNumber):
                            add_to_predecessor(left, rp[0])
                        else:
                            left += rp[0]
                    parts = [0, rp[1]]

            rv = (SnailNumber(left, right), parts)
            logging.debug(f"Returning {rv}")
            return rv

        return visit(self, 0, False)[0]

    def split(self):
        def visit(e, split):
            # Check both our children; if one of them is value >= 10, it breaks
            # apart into a new pair. Otherwise we recurse on any pairs. Note we
            # only split the first number >= 10 we find; after that, this split
            # is done and we try to reduce() again.
            if isinstance(e.left, SnailNumber):
                left, split = visit(e.left, split)
            elif e.left > 9 and not split:
                # Split this number into a pair.
                n = e.left / 2
                left = SnailNumber(math.floor(n), math.ceil(n))
                split = True
            else:
                left = e.left

            if isinstance(e.right, SnailNumber):
                right, split = visit(e.right, split)
            elif e.right > 9 and not split:
                # Same as above.
                n = e.right / 2
                right = SnailNumber(math.floor(n), math.ceil(n))
                split = True
            else:
                right = e.right

            return (SnailNumber(left, right), split)

        return visit(self, False)[0]

    def from_list(l):
        def visit(e):
            if isinstance(e, list):
                return SnailNumber(visit(e[0]), visit(e[1]))
            else:
                return e
        return visit(l)

    def to_list(self):
        def visit(e):
            if isinstance(e, SnailNumber):
                return [visit(e.left), visit(e.right)]
            else:
                return e
        return visit(self)

def read_list(input_file):
    return [SnailNumber.from_list(json.loads(line)) for line in input_file]

def sum_list(input_file):
    return sum(read_list(input_file), start=SnailNumber.identity())

def solve_part1(input_file):
    # In part 1, we're given a list of SnailNumbers. We need to add up all the
    # numbers, then get the magnitude of the result; that's our answer.
    sum_ = sum_list(input_file)
    print(f"Got result: {sum_}")
    print(f"Magnitude: {sum_.magnitude()}")

def solve_part2(input_file):
    # In part 2, we have to find the largest magnitude of any two of the numbers
    # from the homework assignment. We're just going to check all the pairs; if
    # this is too slow, we can try to guide the search somehow.
    numbers = read_list(input_file)
    best_pair = None
    best_magnitude = None
    for i, j in itertools.permutations(range(len(numbers)), 2):
        print(f"Checking indices {i}, {j}.")
        n = numbers[i] + numbers[j]
        mag = n.magnitude()
        if not best_magnitude or mag > best_magnitude:
            print(f"Found new best magnitude: {mag}.")
            best_pair = (i, j)
            best_magnitude = mag

    print(f"Best magnitude was {best_magnitude}.")
    a = numbers[best_pair[0]]
    b = numbers[best_pair[1]]
    best_sum = a + b
    print(f"This was the magnitude of {a} + {b}, which reduces to {best_sum}.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--part",
        type=str,
        choices=["one", "two", "all"],
        default="all",
    )
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()
    if args.part == "one" or args.part == "all":
        solve_part1(args.input_file)
    elif args.part == "two" or args.part == "all":
        solve_part2(args.input_file)

if __name__ == "__main__":
    main()
