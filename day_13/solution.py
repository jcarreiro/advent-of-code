import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import copy
import intcode
import select
import termios
import time
import tty

from collections import defaultdict
from common import Bounds, Point
from enum import auto, IntEnum, Flag

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
        self.segment = 0

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

    def get_segment_value(self):
        return self.segment

    # set the value of the "segment display"
    def set_segment_value(self, v):
        self.segment = v

    # print the screen to stdout
    def print(self):
        # handle the "segment display"
        print(f"Score: {self.segment}")

        # handle the "screen"
        bounds = self.bounds
        padding = 2
        
        # draw top padding
        for _ in range(0, padding):
            print()

        y = bounds.bottom
        while y <= bounds.top:
            row = []
            # draw left padding
            print(' ' * padding, end='')
            x = bounds.left
            while x <= bounds.right:
                row.append(self.get_char_for_tile(self.get_tile_at_point(x, y)))
                x += 1
            print(''.join(row), end='')

            # draw right padding
            print(' ' * padding)
            y += 1

        # draw bottom padding
        for _ in range(0, padding):
            print()

        print()

    def save_state(self):
        return {
            "bounds": self.bounds.save_state(),
            "cells": copy.deepcopy(self.cells),
            "segment": self.segment,
        }

    def restore_state(self, state):
        self.bounds.restore_state(state["bounds"])
        self.cells = copy.deepcopy(state["cells"])
        self.segment = state["segment"]

class ArcadeMachine(object):
    def __init__(self, program, screen=Screen(), input_fn=input):
        self.program = program
        self.screen = screen
        self.input_fn = input_fn

    def _reset(self):
        self.screen.clear()
        self.output_state = OutputState.NEED_X
        self.x = 0
        self.y = 0
        self.im = intcode.IntcodeMachine(
            self.program.copy(),
            input_fn=self.input_fn,
            output_fn=self._draw,
            #debug_flags=intcode.DebugFlags.ALL,
        )
    
    def _draw(self, v):
        if self.output_state == OutputState.NEED_X:
            self.x = v
            self.output_state = OutputState.NEED_Y
        elif self.output_state == OutputState.NEED_Y:
            self.y = v
            self.output_state = OutputState.NEED_TILE_ID
        elif self.output_state == OutputState.NEED_TILE_ID:
            # this is how we address the "segment" display
            if self.x == -1 and self.y == 0:
                self.screen.set_segment_value(v)
            else:
                self.screen.draw(self.x, self.y, v)
            self.output_state = OutputState.NEED_X

    def run(self):
        self._reset()
        self.im.run()

    def save_state(self):
        return {
            'output_state': self.output_state,
            'x': self.x,
            'y': self.y,
            'im': self.im.save_state(),
            'screen': self.screen.save_state(),
        }

    def resume(self, state):
        self.output_state = state['output_state']
        self.x = state['x']
        self.y = state['y']
        self.im.restore_state(state['im'])
        self.screen.restore_state(state['screen'])
        self.im.run() # resume execution

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

# The possible directions for our "pad".
class Direction(Flag):
    NONE = 0
    LEFT = auto()
    RIGHT = auto()

# We need an out-of-band way to signal that we want to roll back the machine
# state -- this is that.
class UndoException(Exception):
    pass

class QuitException(Exception):
    pass

# Reads key presses directly and returns symbolic inputs (like Direction.LEFT).
class GamePad():
    def __enter__(self):
        # Save the terminal settings.
        self.fd = sys.stdin.fileno()
        self.old_term = termios.tcgetattr(self.fd)

        # Switch term to unbuffered by disabling "canonical mode", and disable
        # local echo. See https://man7.org/linux/man-pages/man3/termios.3.html.
        new_term = termios.tcgetattr(self.fd)
        new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, new_term)
        return self

    def __exit__(self, type, value, traceback):
        # Restore original terminal state.
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def _read_key(self):
        c = sys.stdin.buffer.read(1)
        # print(f"Got key: {c}")
        return c

    def read_pad(self):
        c = self._read_key()

        # "secret" keys
        if c == b"u":
            raise UndoException()
        elif c == b"q":
            raise QuitException()

        # arrow keys
        if c == b'\x1b':
            c = self._read_key()
            if c == b'[':
                c = self._read_key()
                if c == b'D':
                    return Direction.LEFT
                elif c == b'C':
                    return Direction.RIGHT

        # ignore all other keys
        return Direction.NONE


def solve_part2():
    screen = Screen()

    # log of all moves made and score
    score = 0
    moves = []
    states = []

    def get_ball_position(state):
        return (state['im']['memory'][2402], state['im']['memory'][2401])

    with GamePad() as game_pad:
        def handle_input(_):
            nonlocal score
            nonlocal moves
            nonlocal m

            # Each time the game asks for input, we print the current "screen"
            # to the console and save the current game state.
            state = m.save_state()
            states.append(state)
            print(f"[input] Pushed state with ball position(?) {get_ball_position(state)}, score {state['screen']['segment']}, {len(states)} states on stack.")
            screen.print()
            s = '0'
            d = game_pad.read_pad()
            if d == Direction.LEFT:
                s = '-1'
            elif d == Direction.RIGHT:
                s = '1'
            moves.append(s)
            return s

        program = intcode.read_initial_memory("input")
        # Per the problem, set address 0 to 2 to enable "free play".
        program[0] = 2
        m = ArcadeMachine(
            program,
            screen=screen,
            input_fn=handle_input,
        )

        while True:
            try:
                # This is not the most elegant solution...
                if states:
                    state = states.pop()
                    print(f"Resume with state at pc: {state['im']['pc']}.")
                    print(f"Ball position(?): {get_ball_position(state)}. score {state['screen']['segment']}.")
                    m.resume(state)
                else:
                    print(f"Reset")
                    m.run()
                # if we get here, the game finished running
                print("Game over, really quit? (y/n)")
                # don't use input() since our term is still set up to not echo
                c = sys.stdin.read(1)
                if c == 'y':
                    break   
            except UndoException:
                # Undo means we want to re-do the previous input. But we pushed just
                # before this input, too, so if we want to re-do the previous input, 
                # we need to remove the top two states on the stack so that we go
                # back to the .
                states.pop()
                print(f"Undo! Popped last state, {len(states)} states left on stack.")
                try:
                    moves.pop()
                except IndexError:
                    pass
            except QuitException:
                break

    print(f"Game ended after {len(moves)} moves, score was {screen.segment}. Moves: {moves}.")
    screen.print() # print final game screen

    # I forgot to print the final score after winning, so I'm bisecting it.
    # 
    # 17134 low
    # 18134 high
    # 17634 ... wrong, didn't say low or high :(

if __name__ == "__main__":
    solve_part2()