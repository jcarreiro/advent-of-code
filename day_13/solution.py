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
        if self.draw_hook:
            self.draw_hook(x, y, tile, self.get_tile_at_point(x, y))
        self.bounds.extend(Point(x, y))
        self.cells[y][x] = tile

    # print the screen to stdout
    def print(self):
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
    # Create an "arcade machine". draw_hook can be used to snoop on draw calls
    # to the "screen".
    def __init__(self, program, draw_hook=None):
        self.program = program
        self.screen = Screen(draw_hook=draw_hook)

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
                self.screen.draw(x, y, v)
                output_state = OutputState.NEED_X

        im = intcode.IntcodeMachine(
            self.program, # memory
            output_fn=draw,
        )
        im.run()

    def print_screen(self):
        self.screen.print()

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
    m = ArcadeMachine(
        program,
        lambda x, y, new_tile, old_tile: count_blocks(new_tile, old_tile),
    )
    m.run()

    # Print the screen, just for fun.
    m.print_screen()

    # Print the count of how many blocks are left.
    print(f"There are {block_count} blocks left on screen.")

if __name__ == "__main__":
    solve_part1()