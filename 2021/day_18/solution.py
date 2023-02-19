#!/usr/bin/env python3

import math

class SnailNumber:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"SnailNumber({self.left!r}, {self.right!r})"

    def __str__(self):
        return f"[{self.left}, {self.right}]"

    def __eq__(self, other):
        if isinstance(other, SnailNumber):
            return self.left == other.left and self.right == other.right
        else:
            return False

    def add(a, b):
        # To add a two SnailNumbers, we first make a new pair from the parts,
        # then we reduce() the number.
        n = SnailNumber(a, b)
        return n.reduce()

    def reduce(self):
        # Repeatedly explode or split until neither action applies.
        a = self
        b = None
        while True:
            print(f"Reducing {a}.")

            # Try to explode.
            b = a.explode()
            if b != a:
                print(f"{a} exploded!")
                a = b
                continue

            # Try to split.
            b = a.split()
            if b != a:
                print(f"{a} split!")
                a = b
                continue

            # If we get here then neither the explode nor the split action
            # changed the number, so we're done with this reduce step.
            print(f"{a} unchanged after explode/split, reduce finished.")
            break

        return a


    def explode(self):
        def visit(n, depth, exploded):
            print(f"Visiting: {n}, depth={depth}, exploded={exploded}.")
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
                print(f"{n} exploded! Returning {rv}.")
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

                parts = []
                if lp:
                    # Our left child exploded. We can add the right part
                    # of the pair to the left child of our right child,
                    # then we need to return the rest up to our parent.
                    print(f"Adding {lp[1]} to {right}.")
                    if lp[1] != 0:
                        if isinstance(n.right, SnailNumber):
                            right.left += lp[1]
                        else:
                            right += lp[1]
                    parts = [lp[0], 0]
                elif rp:
                    # Our right child exploded. We can add the left part
                    # of the pair to the right child of our let child,
                    # then we need to return the rest up to our parent.
                    print(f"Adding {rp[0]} to {left}.")
                    if rp[0] != 0:
                        if isinstance(n.left, SnailNumber):
                            left.right += rp[0]
                        else:
                            left += rp[0]
                    parts = [0, rp[1]]

            rv = (SnailNumber(left, right), parts)
            print(f"Returning {rv}")
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

def main():
    pass

if __name__ == "__main__":
    main()
