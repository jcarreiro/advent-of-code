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
from collections import defaultdict, deque
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
    def __init__(self, program, on_move=None, log_fn=None):
        self.position = Point(0, 0)
        self.last_move = None
        self.im = intcode.IntcodeMachine(program, input_fn=self._input, output_fn=self._output)
        self.on_move = on_move
        self.log_fn = log_fn
        self.map_ = defaultdict(dict)
        # The spaces we know exist (ie. are valid) but whose contents are 
        # UNKNOWN.
        self.frontier = set(self._points_around(Point(0, 0)))
        # If we're pathing to a space, this is set to the current path
        # we're following.
        self.current_path = None
        # The space we start on is EMPTY by definition.
        self._set_tile(Point(0, 0), Tile.EMPTY)        

    def _log(self, msg):
        if self.log_fn:
            self.log_fn(msg)
        else:
            print(msg)

    def _points_around(self, p):
        return [
            p.translate( 0,  1), # N
            p.translate( 1,  0), # E
            p.translate( 0, -1), # S
            p.translate(-1,  0), # W
        ]

    def _add_to_frontier(self, pos):
        # Only add if space is UNKNOWN.
        if self._get_tile(pos) == Tile.UNKNOWN:
            self.frontier.add(pos)

    def _remove_from_frontier(self, pos):
        try:
            self.frontier.remove(pos)
        except KeyError:
            pass

    def _pos_to_move(self, pos, next_pos):
        # we can't move on diagonals
        assert(
            (pos.x == next_pos.x and pos.y != next_pos.y) or
            (pos.x != next_pos.x and pos.y == next_pos.y))
        if pos.y < next_pos.y:
            return Direction.NORTH
        elif pos.y > next_pos.y:
            return Direction.SOUTH
        elif pos.x < next_pos.x:
            return Direction.EAST
        else:
            # pos.x > next_pos.x
            return Direction.WEST

    def _get_tile(self, p):
        try:
            return self.map_[p.y][p.x]
        except KeyError:
            return Tile.UNKNOWN

    def _set_tile(self, p, tile):
        self.map_[p.y][p.x] = tile

    def _get_path_to_closest_unknown_space(self):
        if not self.frontier:
            # No more unexplored spaces.
            raise HaltError()

        def manhattan_distance(p, q):
            return abs(p.x - q.x) + abs(p.y - q.y)

        frontier = sorted(self.frontier, key=lambda p: manhattan_distance(p, self.position))
        target = frontier[0]
        self._log(f"[input] Finding path to target: {target}.")

        def bfs(start_pos, end_pos, grid):
            self._log(f"[bfs] Finding path from {start_pos} to {end_pos}.")
            q = deque([deque([start_pos])])
            while q:
                # Get next path from queue.
                path = q.popleft()

                self._log(f"[bfs] Checking path: {path}")

                # Try to extend path in all cardinal directions.
                n = path[-1]
                moves = [
                    n.translate( 0,  1), # north
                    n.translate( 0, -1), # south
                    n.translate(-1,  0), # west
                    n.translate( 1,  0), # east
                ]
                for move in moves:
                    self._log(f"[bfs] Considering move: {move}")

                    if move == end_pos:
                        # reached target
                        new_path = path.copy()
                        new_path.append(move)
                        self._log(f"[bfs] Done! Returning path {new_path}.")
                        return new_path

                    if move in path:
                        # Skip spaces we've already visited.
                        self._log(f"[bfs] Space {move} already in path")
                        continue

                    
                    tile = self._get_tile(move)
                    if tile == Tile.WALL or tile == Tile.UNKNOWN:
                        # Don't path through WALLs or UNKNOWN spaces.
                        self._log(f"[bfs] Space {move} is {str(tile)}, skipped.")
                        continue

                    # this is a valid next move
                    new_path = path.copy()
                    new_path.append(move)
                    self._log(f"[bfs] Appending path {new_path} to queue.")
                    q.append(new_path)

            # no path to target!
            self._log(f"[bfs] No path from {start_pos} to {end_pos}!")
            return None

        return bfs(self.position, target, self.map_)

    def _input(self, prompt):
        if not self.current_path:
            # Get path to closest unexplored space.
            path = self._get_path_to_closest_unknown_space()
            assert(len(path) > 1)

            # Pop first move off of returned path since it starts with our
            # current position.
            path.popleft()
            self.current_path = path

        # Make a move along the path to the closest unexplored space.
        next_pos = self.current_path.popleft()
        self.last_move = next_pos
        move = self._pos_to_move(self.position, next_pos)
        self._log(f"[input] Moving {str(move)}, new position would be {self.last_move}.")
        return move

    def _output(self, v):
        self._log(f"[output] Got output: {str(Output(v))}.")
        
        # If we're pathing, we should never hit a WALL.
        assert(not self.current_path or (self.current_path and v != Output.WALL))

        # Update map and robot position.
        if v == Output.WALL:
            # We hit a wall; our position did not change.
            self._set_tile(self.last_move, Tile.WALL)
            # If we hit a wall, we can remove the space with the the wall from
            # the set of unexplored spaces.
            self._remove_from_frontier(self.last_move)
        elif v == Output.MOVED:
            # We moved to an empty space.
            self.position = self.last_move
            self._set_tile(self.position, Tile.EMPTY)
            self._remove_from_frontier(self.last_move)
            for p in self._points_around(self.last_move):
                self._add_to_frontier(p)
        elif v == Output.OXYGEN:
            # We moved and found the oxygen system.
            self.position = self.last_move
            self._set_tile(self.position, Tile.OXYGEN)
            self._remove_from_frontier(self.last_move)
            for p in self._points_around(self.last_move):
                self._add_to_frontier(p)
            # TODO: we used to stop here but now we want to explore the whole
            # map; it'd be nice if we could make the code more flexible so
            # that we could do either.
            # raise HaltError()

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

def curses_main(stdscr):
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
            c = '.'
            if r._get_tile(last_pos.translate(-tx, -ty)) == Tile.OXYGEN:
                c = 'O'
            stdscr.addch(last_pos.y, last_pos.x, c)
        else:
            stdscr.addch(ty, tx, '<')

        # draw robot in new position
        stdscr.addch(pos.y, pos.x, '@')

        last_pos = pos

        stdscr.refresh()

    # TODO: show log messages in curses interface
    log_file = open("run.log", "w")
    def log(msg):
        print(msg, file=log_file)

    program = intcode.read_initial_memory("input")
    r = Robot(program, on_move=on_move, log_fn=log)
    r.run()
#    print(f"Robot halted at position ({r.x, r.y}).")

def curses_wrapper():
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        curses_main(stdscr)
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

def main():
    # none curses version, easier to debug
    program = intcode.read_initial_memory("input")
    r = Robot(program)
    r.run()
    print(f"Robot halted at position ({r.position.x, r.position.y}).")

if __name__ == "__main__":
    curses_wrapper()
