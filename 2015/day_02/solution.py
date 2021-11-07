#!/usr/bin/env python3

def paper_needed(l, w, h):
    print(f"paper_needed: Got l={l}, w={w}, h={h}")
    sides = [l*w, w*h, h*l]
    return 2 * sum(sides) + min(sides)

def ribbon_needed(l, w, h):
    print(f"ribbon_needed: Got l={l}, w={w}, h={h}")
    # The ribbon needed is the perimeter of the smallest face, plus
    # a length equal to the volume for the bow.
    return 2 * (l + w + h) - 2 * max([l, w, h]) + l * w * h

def sum_dimensions(f):
    with open("input.txt") as input_file:
        return sum(
            map(
                lambda x: f(*x),
                map(
                    lambda x: map(int, x.strip().split("x")),
                    input_file,
                ),
            ),
        )

def main():
    print(f"Total wrapping paper needed: {sum_dimensions(paper_needed)} sq. ft.")
    print(f"Ribbon needed: {sum_dimensions(ribbon_needed)} ft.")
        
if __name__ == "__main__":
    main()
