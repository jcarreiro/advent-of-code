#!/usr/bin/env python3

import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
# import tracemalloc

from collections import namedtuple
from enum import Enum

Point = namedtuple("Point", ["x", "y"])

# Class used to draw some ASCII art of the problem input. The input grid is huge
# so this is just for fun.
class Grid(object):
    class PenState(Enum):
        UP = 0
        DOWN = 1

    class Bounds:
        def __init__(self):
            self.left = 0
            self.top = 0
            self.right = 0
            self.bottom = 0

        def __str__(self):
            return f"(left = {self.left}, top = {self.top}, right = {self.right}, bottom = {self.bottom})"

    def __init__(self):
        self.canvas = [['O']]
        # Bounds of canvas, inclusive of endpoints.
        self.bounds = Grid.Bounds()
        self.pen_pos = Point(0, 0) # pen starts at the origin
        self.pen_state = Grid.PenState.UP # pen starts up

    def get_pen_pos(self):
        return self.pen_pos

    def pen_down(self):
        self.pen_state = Grid.PenState.DOWN

    def pen_up(self):
        self.pen_state = Grid.PenState.UP

    def move_to(self, p: Point):
        # We only need to support horizontal and vertical lines so that's all we
        # do.
        if self.pen_state == Grid.PenState.DOWN and p.x != self.pen_pos.x and p.y != self.pen_pos.y:
            raise ValueError("Only horizontal and vertical lines are supported!")

        # Ensure canvas is big enough to contain destination point. We do not
        # use list multiplication below to avoid aliasing of the created lists,
        # even though it would be more concise.
        if self.bounds.left > p.x:
            print(f"Left bound {self.bounds.left} > p.x {p.x}, resizing canvas.")
            for i in range(len(self.canvas)):
                self.canvas[i] = ['.' for j in range(self.bounds.left - p.x)] + self.canvas[i]
            self.bounds.left = p.x
        if self.bounds.right < p.x:
            print(f"Right bound {self.bounds.right} < p.x {p.x}, resizing canvas.")
            for i in range(len(self.canvas)):
                self.canvas[i] = self.canvas[i] + ['.' for j in range(p.x - self.bounds.right)]
            self.bounds.right = p.x
        if self.bounds.bottom > p.y:
            print(f"Bottom bound {self.bounds.bottom} > p.y {p.y}, resizing canvas.")
            self.canvas = [['.' for k in range(self.bounds.right - self.bounds.left + 1)] for j in range(self.bounds.bottom - p.y)] + self.canvas
            self.bounds.bottom = p.y
        if self.bounds.top < p.y:
            print(f"Top bound {self.bounds.top} < p.y {p.y}, resizing canvas.")
            self.canvas = self.canvas[:] + [['.' for k in range(self.bounds.right - self.bounds.left + 1)] for j in range(p.y - self.bounds.top)]
            self.bounds.top = p.y

        if self.pen_state == Grid.PenState.DOWN:
            if p.x != self.pen_pos.x:
                x0 = min(self.pen_pos.x, p.x) - self.bounds.left
                x1 = max(self.pen_pos.x, p.x) - self.bounds.left
                y = self.pen_pos.y - self.bounds.bottom
                print(f"Canvas dimensions are {len(self.canvas)} rows, {len(self.canvas[0])} cols.")
                print(f"Getting row {self.pen_pos.y} ({y}), bounds are {self.bounds}.")
                row = self.canvas[y]
                print(f"Row has len {len(row)}.")
                for x in range(x0, x1+1):
                    c = row[x]
                    assert(c in 'O.|')
                    print(f"Got character {c} at cell {x,y}.")
                    if c == '.':
                        c = '-' # horizontal line
                    elif c == '|':
                        c = '+' # intersection
                    # all other symbols (e.g. 'O') are unchanged
                    print(f"Set cell {x,y} to character {c}.")
                    row[x] = c
            elif p.y != self.pen_pos.y:
                y0 = min(self.pen_pos.y, p.y) - self.bounds.bottom
                y1 = max(self.pen_pos.y, p.y) - self.bounds.bottom
                x = self.pen_pos.x - self.bounds.left
                for y in range(y0, y1+1):
                    c = self.canvas[y][x]
                    assert(c in 'O.-')
                    print(f"Got character {c} at cell {x,y}.")
                    if c == '.':
                        c = '|' # vertical line
                    elif c == '-':
                        c = '+' # intersection
                    # all other symbols (e.g. 'O') are unchanged
                    print(f"Set cell {x,y} to character {c}.")
                    self.canvas[y][x] = c

        self.pen_pos = p

    def show(self, file=sys.stdout):
        # note that we store the grid with +y "down", so we need to reverse it
        # here
        print(''.join(['.'] * (self.bounds.right - self.bounds.left + 3)), file=file)
        for y in range(len(self.canvas) - 1, -1, -1):
            print(''.join(['.'] + self.canvas[y] + ['.']), file=file)
        print(''.join(['.'] * (self.bounds.right - self.bounds.left + 3)), file=file)

    def save(self, path):
        # dump canvas to a file
        with open(path, 'w') as file:
            self.show(file=file)

class Bounds:
    def __init__(self, left = 0, top = 0, right = 0, bottom = 0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __eq__(self, other):
        return self.left == other.left and self.top == other.top and self.right == other.right and self.bottom == other.bottom

    def __str__(self):
        return f"(left = {self.left}, top = {self.top}, right = {self.right}, bottom = {self.bottom})"

    # Return new bounds object which includes point. If this object already
    # includes point, returns this object, unmodified. Assumes +y is up.
    def extend(self, p: Point):
        return Bounds(
            min(self.left, p.x),
            max(self.top, p.y),
            max(self.right, p.x),
            min(self.bottom, p.y))

# OpenCV version of Grid class; creates a viewable image.
class ImageGrid(object):
    class PenState(Enum):
        UP = 0
        DOWN = 1

    def __init__(self, bounds):
        assert(bounds.top > bounds.bottom)
        assert(bounds.right > bounds.left)

        rows = bounds.top - bounds.bottom + 1
        cols = bounds.right - bounds.left + 1
        self.canvas = np.full((rows, cols, 3), 255, dtype='uint8')
        print(f"Created canvas with shape {self.canvas.shape}, size {self.canvas.nbytes}.")

        self.bounds = bounds
        self.pen_pos = Point(0, 0) # pen starts at the origin
        self.pen_state = Grid.PenState.UP # pen starts up
        self.pen_color = (255, 255, 255) # white

    def set_pen_color(self, color):
        self.pen_color = color

    def get_pen_pos(self):
        return self.pen_pos

    def pen_down(self):
        self.pen_state = Grid.PenState.DOWN

    def pen_up(self):
        self.pen_state = Grid.PenState.UP

    @profile
    def adjust_bounds(self, new_bounds: Bounds):
        # We don't handle shrinking the bounds ATM.
        assert(new_bounds.left <= self.bounds.left)
        assert(new_bounds.top >= self.bounds.top)
        assert(new_bounds.right >= self.bounds.right)
        assert(new_bounds.bottom <= self.bounds.bottom)

        print(f"Adjusting bounds from {self.bounds} to {new_bounds}.")
        print(f"Canvas shape was {self.canvas.shape}, size was {self.canvas.nbytes}.")

        # Pad on left and right using hstack.
        rows = self.canvas.shape[0]
        left_pad = abs(new_bounds.left - self.bounds.left)
        if left_pad > 0:
            self.canvas = np.hstack((
                np.full((rows, left_pad, 3), 255, dtype='uint8'),
                self.canvas,
            ))

        right_pad = abs(new_bounds.right - self.bounds.right)
        if right_pad > 0:
            self.canvas = np.hstack((
                self.canvas,
                np.full((rows, right_pad, 3), 255, dtype='uint8'),
            ))

        # Pad on top and bottom using vstack.
        cols = self.canvas.shape[1]
        top_pad = abs(new_bounds.top - self.bounds.top)
        if top_pad > 0:
            self.canvas = np.vstack((
                self.canvas,
                np.full((top_pad, cols, 3), 255, dtype='uint8'),
            ))

        bottom_pad = abs(new_bounds.bottom - self.bounds.bottom)
        if bottom_pad > 0:
            self.canvas = np.vstack((
                np.full((bottom_pad, cols, 3), 255, dtype='uint8'),
                self.canvas,
            ))

        print(f"Canvas shape is now {self.canvas.shape}, size is {self.canvas.nbytes}.")
        # s = input("Continue (C) or quit (Q)? ")
        # if s == "q" or s == "Q":
        #     exit()

    @profile
    def move_to(self, p: Point):
        print(f"Move to {p} from {self.pen_pos}, pen state is {self.pen_state}.")

        assert(self.bounds.left <= p.x and p.x <= self.bounds.right)
        assert(self.bounds.bottom <= p.y and p.y <= self.bounds.top)

        # See comment below about memory leak when adjusting bounds.
        #
        # new_bounds = self.bounds.extend(p)
        # if self.bounds != new_bounds:
        #     self.adjust_bounds(new_bounds)
        #    self.bounds = new_bounds

        if self.pen_state == Grid.PenState.DOWN:
            x0 = self.pen_pos.x - self.bounds.left
            y0 = self.pen_pos.y - self.bounds.bottom
            x1 = p.x - self.bounds.left
            y1 = p.y - self.bounds.bottom
            cv2.line(self.canvas, (x0, y0), (x1, y1), self.pen_color, 1)

        self.pen_pos = p

    def scale_and_flip_image(self, img, w, h):
        # Scale so image is at least (w, h) size, preserving aspect ratio.
        r, c, d = img.shape
        fx = float(w) / float(c)
        fy = float(h) / float(r)
        print(f"Original size {(c, r)}, desired minimum size {(w, h)}.")
        print(f"Scale factors fx = {fx}, fy = {fy}.")
        s = max(fx, fy)
        if s > 1.0:
            print(f"Using scale factor {s}.")
            img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_NEAREST)
        return cv2.flip(img, 0)

    def show(self):
        cv2.imshow('image', self.scale_and_flip_image(self.canvas, 200, 200))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def save(self, path):
        cv2.imwrite(path, self.scale_and_flip_image(self.canvas, 200, 200))

# Converts a wire direction (e.g. "R10") into a position, given a starting
# position.
def wire_direction_to_position(pos: Point, inst: str):
    direction = inst[0]
    distance = int(inst[1:])

    assert(direction in "RDLU")
    assert(distance > 0)

    # print(f"Moving from {pos}, direction {direction}, distance {distance}.")

    if direction == 'R':
        new_pos = Point(pos.x + distance, pos.y)
    elif direction == 'D':
        new_pos = Point(pos.x, pos.y - distance)
    elif direction == 'L':
        new_pos = Point(pos.x - distance, pos.y)
    elif direction == 'U':
        new_pos = Point(pos.x, pos.y + distance)

    # print(f"New pos is {new_pos}.")
    return new_pos

def wire_directions_to_points(directions):
    p = Point(0, 0)
    points = [p]
    for d in directions:
        p = wire_direction_to_position(p, d)
        points.append(p)
    return points

@profile
def draw_wires(wires, path=None):
    # For some reason repeatedly adjusting the bounds of the np.array which
    # backs the ImageGrid (using hstack and vstack) "leaks" a lot of memory
    # (the memory used by this process spikes to ~19 GB, which is much more
    # than the actual np.array is using, according to .nbytes). So we do a
    # first pass over the wire here to find appropriate bounds, so that we
    # can size the array correctly to start with.
    wires = [wire_directions_to_points(w) for w in wires]
    left = top = right = bottom = 0
    for w in wires:
        for p in w:
            left = min(left, p.x)
            top = max(top, p.y)
            right = max(right, p.x)
            bottom = min(bottom, p.y)
    padding = 5
    bounds = Bounds(left - padding, top + padding, right + padding, bottom - padding)
    print(f"Got bounds {bounds}.")

    colors = [
        [0, 0, 255], # opencv assumes BGR order
        [0, 255, 0],
    ]
    grid = ImageGrid(bounds)
    for i in range(len(wires)):
        grid.set_pen_color(colors[i])
        grid.pen_up()
        grid.move_to(Point(0, 0))
        for p in wires[i]:
            grid.pen_down()
            grid.move_to(p)
            grid.pen_up()
    if path:
        print(f"Saving image to {path}.")
        grid.save(path)
    else:
        grid.show()

def manhattan_dist(p0: Point, p1: Point):
    return abs(p1.x - p0.x) + abs(p1.y - p0.y)

def solve_part1(wires):
    Segment = namedtuple("Segment", ["x0", "y0", "x1", "y1"])

    def convert_wire(wire):
        segments = []
        pos = Point(0, 0)
        for inst in wire:
            new_pos = wire_direction_to_position(pos, inst)
            # segments must be horizontal or vertical
            assert((pos.x == new_pos.x and pos.y != new_pos.y) or
                   (pos.x != new_pos.x and pos.y == new_pos.y))
            x0 = min(pos.x, new_pos.x)
            x1 = max(pos.x, new_pos.x)
            y0 = min(pos.y, new_pos.y)
            y1 = max(pos.y, new_pos.y)
            segments.append(Segment(x0, y0, x1, y1))
            pos = new_pos
        return segments

    wires = list(map(convert_wire, wires))
    assert(len(wires) == 2)
    print(wires)

    hs = sorted(filter(lambda s: s.y0 == s.y1, wires[1]), key=lambda s: s.y0)
    vs = sorted(filter(lambda s: s.x0 == s.x1, wires[1]), key=lambda s: s.x0)
    print(hs, vs)

    min_distance = None
    best_intersection = Point(0, 0)
    for s0 in wires[0]:
        print(f"Checking segment {s0}.")
        if s0.x0 == s0.x1:
            print(f"  Segment is vertical (x = {s0.x0}).")
            for s1 in hs:
                assert(s1.y0 == s1.y1)
                print(f"  Comparing to segment {s1}.")
                if s1.y0 < s0.y0:
                    # h seg is below us
                    print("  Segment below, continuing.")
                    continue
                elif s1.y0 >= s0.y0 and s1.y0 <= s0.y1:
                    # h seg inside our bounds, check other coord
                    print("  Possible match.")
                    if s1.x0 <= s0.x0 and s1.x1 >= s0.x0:
                        p = Point(s0.x0, s1.y0)
                        d = manhattan_dist(p, Point(0, 0))
                        print("  Intersection found at point {p}, Manhattan distance {d}.")
                        if not min_distance or d < min_distance:
                            best_intersection = p
                            min_distance = d
                else:
                    # h seg must be above us
                    print("  Segment above, breaking loop.")
                    break
        elif s0.y0 == s0.y1:
            print(f"  Segment is horizontal (y = {s0.y0}).")
            for s1 in vs:
                assert(s1.x0 == s1.x1)
                print(f"  Comparing to segment {s1}.")
                if s1.x0 < s0.x0:
                    print(" Segment to the left, continuing.")
                    continue
                elif s1.x0 >= s0.x0 and s1.x0 <= s0.x1:
                    print("  Possible match.")
                    if s1.y0 <= s0.y0 and s1.y1 >= s0.y0:
                        p = Point(s1.x0, s0.y0)
                        d = manhattan_dist(p, Point(0, 0))
                        print("  Intersection found at point {p}, Manhattan distance {d}.")
                        if not min_distance or d < min_distance:
                            best_intersection = p
                            min_distance = d
                else:
                    print(" Segment to the right, breaking loop.")
                    break
        else:
            raise ValueError("Segment {s0} x and y both vary!")
    print(f"Closest intersection point to origin is {best_intersection} (distance {min_distance}).")

# Test cases from the problem.
test_cases = [
    {
        "wires": [["R8","U5","L5","D3"], ["U7","R6","D4","L4"]],
        "solution": 6,
    },
    {
        "wires": [
            ["R75","D30","R83","U83","L12","D49","R71","U7","L72"],
            ["U62","R66","U55","R34","D71","R55","D58","R83"],
        ],
        "solution": 159,
    },
    {
        "wires": [
            ["R98","U47","R26","D63","R33","U87","L62","D20","R33","U53","R51"],
            ["U98","R91","D20","R16","D67","R40","U7","R15","U6","R7"],
        ],
        "solution": 135,
    },
]

if __name__ == "__main__":
    with open("input", "r") as f:
        wires = [l.rstrip().split(",") for l in f]
    print(wires)

    # wires = test_cases[0]["wires"]
    # print(wires)

    draw_wires(wires, "wires.png")
    solve_part1(wires)
