#!/usr/bin/env python3
#
# On day 15, we're using a robot to repair our oxygen system:
#
#   According to the readouts, the oxygen system must have failed days ago after
#   a rupture in oxygen tank two; that section of the ship was automatically
#   sealed once oxygen levels went dangerously low. A single remotely-operated
#   repair droid is your only option for fixing the oxygen system.
#
# The robot accepts movement commands as input: north (1), south (2), west (3),
# and east (4). It returns a status as output:
#
#   - 0: The repair droid hit a wall. Its position has not changed.
#
#   - 1: The repair droid has moved one step in the requested direction.
#
#   - 2: The repair droid has moved one step in the requested direction; its new
#     position is the location of the oxygen system.
#
# In the first part of the exercise, our goal is to find the oxygen system.

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import curses
import intcode
import random

from common import Point
from collections import defaultdict
from enum import IntEnum

class Tile(IntEnum):
    WALL = 0  # droid hit a wall trying to enter this space
    EMPTY = 1  # droid can move through this space
    OXYGEN = 2  # space contains oxygen system (goal space)
    UNKNOWN = 3  # unexplored space

class Direction(IntEnum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4

class Output(IntEnum):
    WALL = 0  # droid hit a wall
    MOVED = 1  # moved to requested space
    OXYGEN = 2  # moved and found oxygen system

# Used to HALT to robot when we reach the goal space.
class HaltError(Exception):
    pass

class Robot(object):
    def __init__(self, program, on_move=None):
        self.position = Point(0, 0)
        self.last_move = None
        self.im = intcode.IntcodeMachine(program, input_fn=self._input, output_fn=self._output)
        self.on_move = on_move
        self.map_ = defaultdict(dict)
        # The spaces we know exist (ie. are valid) but which are UNKNOWN.
        # To start with this is all the spaces around the origin. Each
        # time we visit a new space (a space that was UNKNOWN and which
        # we discover is EMPTY) we add any spaces around it to this set
        # which aren't already known.
        self.frontier = set(self._points_around(Point(0, 0)))
        # The space we start on is EMPTY by definition.
        self._set_tile(Point(0, 0), Tile.EMPTY)

    def _points_around(self, p):
        return [
            p.translate( 0,  1), # N
            p.translate( 1,  1), # NE
            p.translate( 1,  0), # E
            p.translate( 1, -1), # SE
            p.translate( 0, -1), # S
            p.translate(-1, -1), # SW
            p.translate(-1,  0), # W
            p.translate(-1,  1), # NW
        ]

    def _get_tile(self, p):
        try:
            return self.map_[p.y][p.x]
        except KeyError:
            return Tile.UNKNOWN

    def _set_tile(self, p, tile):
        self.map_[p.y][p.x] = tile

    def _input(self, prompt):
        # Pick an unexplored direction and return it. If we've explored all the
        # spaces around us, move towards a space we haven't explored yet.
        #
        # TODO: move toward the closest unexplored space instead of a random
        # unexplored space.
        directions = {
            Direction.NORTH: self.position.translate( 0,  1),
            Direction.SOUTH: self.position.translate( 0, -1),
            Direction.WEST:  self.position.translate(-1,  0),
            Direction.EAST:  self.position.translate( 1,  0),
        }
        move = random.choice(list(Direction))
        for d in Direction:
            p = directions[d]
            if self._get_tile(p) == Tile.UNKNOWN:
                move = d

        # Save where we tried to go for use when we read robot output.
        self.last_move = directions[move]
#        print(f"Moving {str(move)}, new position would be {self.last_move}.")
        return move

    def _output(self, v):
#        print(f"Got output: {str(Output(v))}.")
        # Update map and robot position.
        if v == Output.WALL:
            # We hit a wall; our position did not change.
            self._set_tile(self.last_move, Tile.WALL)
        elif v == Output.MOVED:
            # We moved to an empty space.
            self.position = self.last_move
            self._set_tile(self.position, Tile.EMPTY)
        elif v == Output.OXYGEN:
            # We moved and found the oxygen system.
            self.position = self.last_move
            self._set_tile(self.position, Tile.OXYGEN)
            raise HaltError()

        if self.on_move:
            self.on_move(self.position, self.last_move, v)

    def run(self):
        # We should think about how to handle the case where we never find the
        # goal state (e.g. there is not path) -- right now the robot will search
        # "forever".
        try:
            self.im.run()
        except HaltError:
            pass

def main(stdscr):
    stdscr.clear()

    # Seed random so that we always get the same sequence of random choices
    # for the robot.
    random.seed(0)

    # The last known position of the robot.
    last_pos = Point(0, 0)

    # This is the origin in our "screen coordinates".
    tx = curses.COLS // 2
    ty = curses.LINES // 2

    def on_move(pos, last_move, result):
        nonlocal last_pos
        pos = pos.translate(tx, ty)
        last_move = last_move.translate(tx, ty)
        if result == Output.WALL:
            stdscr.addch(last_move.y, last_move.x, '#')

        # fix up old robot position, unless it's the origin.
        if last_pos != Point(tx, ty):
            stdscr.addch(last_pos.y, last_pos.x, '.')
        else:
            stdscr.addch(ty, tx, '<')

        # draw robot in new position
        stdscr.addch(pos.y, pos.x, '@')

        last_pos = pos

        stdscr.refresh()

    program = intcode.read_initial_memory("input")
    r = Robot(program, on_move=on_move)
    r.run()
#    print(f"Robot halted at position ({r.x, r.y}).")

if __name__ == "__main__":
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        main(stdscr)
    finally:
        stdscr.addstr(curses.LINES - 1, 0, "Be seeing you...")
        stdscr.refresh()
        stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.reset_shell_mode()
        print()
        # Don't call endwin since this clears the screen.
        # curses.endwin()
