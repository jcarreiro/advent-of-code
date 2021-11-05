# Fix up sys.path so we can find intcode. Python imports suck.
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import intcode

from collections import defaultdict
from common import Point
from copy import deepcopy
from enum import IntEnum

class Color(IntEnum):
    BLACK = 0
    WHITE = 1

class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class Bounds:
    def __init__(self):
        self.top = 0
        self.right = 0
        self.bottom = 0
        self.left = 0

    def extend(self, p):
        self.top = max(self.top, p.y)
        self.right = max(self.right, p.x)
        self.bottom = min(self.bottom, p.y)
        self.left = min(self.left, p.x)
        print(f"New bounds are {(self.top, self.right, self.bottom, self.left)}.")

# The "hull".
class Grid:
    def __init__(self):
        self.cells = defaultdict(dict)
        self.bounds = Bounds()

    # Note that the bound are effectively infinite since we extend them on any
    # call to set. This is a way to get the area that's actually been painted.
    def get_bounds(self):
        return self.bounds

    def get_cell(self, p):
        try:
            return self.cells[p.y][p.x]
        except:
            return Color.BLACK

    def set_cell(self, p, color):
        self.cells[p.y][p.x] = color
        self.bounds.extend(p)

# Hull painting robot.
class Robot:
    def __init__(self, program, grid, pos, facing, paint_cb):
        # TODO: intcode machine for "brain"
        self.program = program
        self.grid = grid
        self.pos = pos
        self.facing = facing
        self.paint_cb = paint_cb

    def get_pos(self):
        return self.pos

    def get_facing(self):
        return self.facing

    def run(self):
        # unused argument here is input prompt
        def camera(_):
            # Note Intcode machine expects input to be string
            return str(int(self.grid.get_cell(self.pos)))

        def paint(color):
            # 0 means paint black, 1 means paint white
            self.grid.set_cell(self.pos, Color(color))
            self.paint_cb(self.pos)
            print(f"Robot painted cell {self.pos} {str(Color(color))}.")

        def turn(direction):
            # 0 means 90 deg left, 1 means 90 deg right
            rules = {
                Direction.UP: (Direction.LEFT, Direction.RIGHT),
                Direction.RIGHT: (Direction.UP, Direction.DOWN),
                Direction.DOWN: (Direction.RIGHT, Direction.LEFT),
                Direction.LEFT: (Direction.DOWN, Direction.UP),
            }
            new_facing = rules[self.facing][direction]
            print(f"Robot turned from {str(self.facing)} to {str(new_facing)}.")
            self.facing = new_facing

        class OutputState(IntEnum):
            NEED_PAINT = 0
            NEED_MOVE = 1

        output_state = OutputState.NEED_PAINT

        def output(v):
            nonlocal output_state
            if output_state == OutputState.NEED_PAINT:
                paint(v)
                output_state = OutputState.NEED_MOVE
            elif output_state == OutputState.NEED_MOVE:
                turn(v)
                self.move()
                self.draw_grid()
                output_state = OutputState.NEED_PAINT

        im = intcode.IntcodeMachine(
            self.program, # memory
            camera, # input_fn
            output, # output_fn
        )
        im.run()

    def move(self):
        new_pos = None
        if self.facing == Direction.UP:
            # Note that, as usual with these problems, up is -y.
            new_pos = Point(self.pos.x, self.pos.y - 1)
        elif self.facing == Direction.RIGHT:
            new_pos = Point(self.pos.x + 1, self.pos.y)
        elif self.facing == Direction.DOWN:
            new_pos = Point(self.pos.x, self.pos.y + 1)
        elif self.facing == Direction.LEFT:
            new_pos = Point(self.pos.x - 1, self.pos.y)
        else:
            assert("Unknown direction: {self.facing}")
        print(f"Robot moved from {self.pos} to {new_pos}.")
        self.pos = new_pos

    def draw_grid(self):
        def get_char_for_facing(facing):
            if facing == Direction.UP:
                return '^'
            if facing == Direction.RIGHT:
                return '>'
            if facing == Direction.DOWN:
                return 'v'
            if facing == Direction.LEFT:
                return '<'

        bounds = self.grid.get_bounds()
        padding = 2
        y = bounds.bottom - padding
        while y <= bounds.top + padding:
            row = []
            x = bounds.left - padding
            while x <= bounds.right + padding:
                if x == self.pos.x and y == self.pos.y:
                    row.append(get_char_for_facing(self.facing))
                elif self.grid.get_cell(Point(x, y)) == Color.BLACK:
                    row.append('.')
                else:
                    row.append('#')
                x += 1
            print(''.join(row))
            y += 1
        print()
# End of Robot class

if __name__ == "__main__":
    program = intcode.read_initial_memory("input")
    panels_painted = set()
    grid = Grid()
    # In part 2 initial square is white
    grid.set_cell(Point(0, 0), Color.WHITE)
    robot = Robot(program, grid, Point(0, 0), Direction.UP, lambda p: panels_painted.add(p))
    robot.run()
    print(f"The number of panels painted at least once is: {len(panels_painted)}.")
