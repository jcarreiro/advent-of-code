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

import intcode
import random

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
    def __init__(self, program):
        self.x = 0
        self.y = 0
        self.last_move = None
        self.im = intcode.IntcodeMachine(program, input_fn=self._input, output_fn=self._output)
        self.map_ = defaultdict(dict)
        # The space we start on is EMPTY by definition.
        self._set_tile(0, 0, Tile.EMPTY)

    def _get_tile(self, x, y):
        try:
            return self.map_[y][x]
        except KeyError:
            return Tile.UNKNOWN

    def _set_tile(self, x, y, tile):
        self.map_[y][x] = tile

    def _input(self, prompt):
        # Pick an unexplored direction and return it. If we've explored all the
        # spaces around us, pick a random direction.
        #
        # TOOD: do something smarter in the latter case, e.g. move toward the
        # nearest UNKNOWN space.
        directions = {
            Direction.NORTH: (self.x    , self.y + 1),
            Direction.SOUTH: (self.x    , self.y - 1),
            Direction.WEST:  (self.x - 1, self.y    ),
            Direction.EAST:  (self.x + 1, self.y    ),
        }
        move = random.choice(list(Direction))
        for d in Direction:
            x, y = directions[d]
            if self._get_tile(x, y) == Tile.UNKNOWN:
                move = d

        # Save where we tried to go for use when we read robot output.
        self.last_move = directions[move]
        print(f"Moving {str(move)}, new position would be {self.last_move}.")
        return move

    def _output(self, v):
        print(f"Got output: {str(Output(v))}.")
        # Update map and robot position.
        if v == Output.WALL:
            # We hit a wall; our position did not change.
            x, y = self.last_move
            self._set_tile(x, y, Tile.WALL)
        elif v == Output.MOVED:
            # We moved to an empty space.
            self.x, self.y = self.last_move
            self._set_tile(self.x, self.y, Tile.EMPTY)
        elif v == Output.OXYGEN:
            # We moved and found the oxygen system.
            self.x, self.y = self.last_move
            self._set_tile(self.x, self.y, Tile.OXYGEN)
            raise HaltError()

    def run(self):
        # We should think about how to handle the case where we never find the
        # goal state (e.g. there is not path) -- right now the robot will search
        # "forever".
        try:
            self.im.run()
        except HaltError:
            pass

if __name__ == "__main__":
    program = intcode.read_initial_memory("input")
    r = Robot(program)
    r.run()
    print(f"Robot halted at position ({r.x, r.y}).")
