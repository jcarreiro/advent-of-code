import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import intcode

from collections import defaultdict
from common import Bounds, Point
from enum import IntEnum

class OutputState(IntEnum):
    NEED_X = 0
    NEED_Y = 1
    NEED_TILE_ID = 2

class TileSet(IntEnum):
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    H_PADDLE = 3
    BALL = 4    

class Screen(object):
    def __init__(self, draw_hook=None):
        self.clear()
        self.draw_hook = draw_hook

    def clear(self):
        self.bounds = Bounds()
        self.cells = defaultdict(dict)
        self.segment = ''

    def get_char_for_tile(self, tile):
        tiles = {
            TileSet.EMPTY: ' ',    # empty tile
            TileSet.WALL: '#',     # indestructible
            TileSet.BLOCK: '%',    # can be broken by ball
            TileSet.H_PADDLE: '-', # paddle
            TileSet.BALL: '*',     # ball
        }
        return tiles[tile]
    
    def get_tile_at_point(self, x, y):
        try:
            return self.cells[y][x]
        except:
            return TileSet.EMPTY

    # "draw" a tile onto the screen
    def draw(self, x, y, tile):
        # x = -1 is how we address the "segment display", so we assume that
        # all valid draw commands have x, y >= 0.
        assert(x >= 0)
        assert(y >= 0)
        if self.draw_hook:
            self.draw_hook(x, y, tile, self.get_tile_at_point(x, y))
        self.bounds.extend(Point(x, y))
        self.cells[y][x] = tile

    # set the value of the "segment display"
    def set_segment_value(self, v):
        self.segment = str(v)

    # print the screen to stdout
    def print(self):
        # handle the "segment display"
        print(f"Score: {self.segment}")

        # handle the "screen"
        bounds = self.bounds
        padding = 2
        y = bounds.bottom - padding
        while y <= bounds.top + padding:
            row = []
            x = bounds.left - padding
            while x <= bounds.right + padding:
                row.append(self.get_char_for_tile(self.get_tile_at_point(x, y)))
                x += 1
            print(''.join(row))
            y += 1
        print()

# Same basic idea here as the hull painting robot from problem 11.
class ArcadeMachine(object):
    def __init__(self, program, screen=Screen(), input_fn=input):
        self.program = program
        self.screen = screen
        self.input_fn = input_fn

    def run(self):
        self.screen.clear()

        output_state = OutputState.NEED_X
        x = 0
        y = 0

        def draw(v):
            nonlocal output_state, x, y
            if output_state == OutputState.NEED_X:
                x = v
                output_state = OutputState.NEED_Y
            elif output_state == OutputState.NEED_Y:
                y = v
                output_state = OutputState.NEED_TILE_ID
            elif output_state == OutputState.NEED_TILE_ID:
                # this is how we address the "segment" display
                if x == -1 and y == 0:
                    self.screen.set_segment_value(v)
                else:
                    self.screen.draw(x, y, v)
                output_state = OutputState.NEED_X

        im = intcode.IntcodeMachine(
            self.program, # memory
            input_fn=self.input_fn,
            output_fn=draw,
        )
        im.run()

def solve_part1():
    # Run the program and count how many block tiles are on the screen when the
    # game exits.
    block_count = 0
    def count_blocks(new_tile, old_tile):
        nonlocal block_count
        if new_tile == TileSet.BLOCK and old_tile == TileSet.BLOCK:
            # no change in block count
            pass
        elif new_tile == TileSet.BLOCK and old_tile != TileSet.BLOCK:
            # we just wrote a block to a cell that didn't have one before
            block_count += 1
        elif new_tile != TileSet.BLOCK and old_tile == TileSet.BLOCK:
            # we replaced a block with a non-block
            block_count -= 1
        elif new_tile != TileSet.BLOCK and old_tile != TileSet.BLOCK:
            # no change in block count
            pass
    
    program = intcode.read_initial_memory("input")
    screen = Screen(draw_hook=lambda x, y, new_tile, old_tile: count_blocks(new_tile, old_tile))
    m = ArcadeMachine(program, screen)
    m.run()

    # Print the screen, just for fun.
    screen.print()

    # Print the count of how many blocks are left.
    print(f"There are {block_count} blocks left on screen.")

def solve_part2():
    screen = Screen()

    def handle_input(_):
        # each time the game asks for input, we print the current "screen"
        # to the console
        screen.print()
        print("-1 = move left, 0 = don't move, 1 = move right")
        return input("> ")

    program = intcode.read_initial_memory("input")
    # Set address 0 to 2 to enable "free play".
    program[0] = 2
    m = ArcadeMachine(
        program,
        screen=screen,
        input_fn=handle_input,
    )
    m.run()

if __name__ == "__main__":
    solve_part2()