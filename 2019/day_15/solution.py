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
import time

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

class Map(object):
    def __init__(self):
        self.map_ = defaultdict(dict)

    def get_tile(self, p):
        try:
            return self.map_[p.y][p.x]
        except KeyError:
            return Tile.UNKNOWN

    def set_tile(self, p, tile):
        self.map_[p.y][p.x] = tile


def points_around(p):
    return [
        p.translate( 0,  1), # N
        p.translate( 1,  0), # E
        p.translate( 0, -1), # S
        p.translate(-1,  0), # W
    ]
    
def bfs(start_pos, end_pos, map, log_fn=lambda _: None):
    log_fn(f"[bfs] Finding path from {start_pos} to {end_pos}.")
    q = deque([deque([start_pos])])
    while q:
        # Get next path from queue.
        path = q.popleft()

        log_fn(f"[bfs] Checking path: {path}")

        # Try to extend path in all cardinal directions.
        n = path[-1]
        moves = points_around(n)
        for move in moves:
            log_fn(f"[bfs] Considering move: {move}")

            if move == end_pos:
                # reached target
                new_path = path.copy()
                new_path.append(move)
                log_fn(f"[bfs] Done! Returning path {new_path}.")
                return new_path

            if move in path:
                # Skip spaces we've already visited.
                log_fn(f"[bfs] Space {move} already in path")
                continue

            
            tile = map.get_tile(move)
            if tile == Tile.WALL or tile == Tile.UNKNOWN:
                # Don't path through WALLs or UNKNOWN spaces.
                log_fn(f"[bfs] Space {move} is {str(tile)}, skipped.")
                continue

            # this is a valid next move
            new_path = path.copy()
            new_path.append(move)
            log_fn(f"[bfs] Appending path {new_path} to queue.")
            q.append(new_path)

    # no path to target!
    log_fn(f"[bfs] No path from {start_pos} to {end_pos}!")
    return None

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
        self.map_ = Map()
        # The spaces we know exist (ie. are valid) but whose contents are 
        # UNKNOWN.
        self.frontier = set(points_around(Point(0, 0)))
        # If we're pathing to a space, this is set to the current path
        # we're following.
        self.current_path = None
        # The space we start on is EMPTY by definition.
        self.map_.set_tile(Point(0, 0), Tile.EMPTY)        

    def _log(self, msg):
        if self.log_fn:
            self.log_fn(msg)
        else:
            print(msg)

    def _add_to_frontier(self, pos):
        # Only add if space is UNKNOWN.
        if self.map_.get_tile(pos) == Tile.UNKNOWN:
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

    def _get_path_to_closest_unknown_space(self):
        if not self.frontier:
            # No more unexplored spaces.
            raise HaltError()

        def manhattan_distance(p, q):
            return abs(p.x - q.x) + abs(p.y - q.y)

        frontier = sorted(self.frontier, key=lambda p: manhattan_distance(p, self.position))
        target = frontier[0]
        self._log(f"[input] Finding path to target: {target}.")
        return bfs(self.position, target, self.map_, self._log)

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
            self.map_.set_tile(self.last_move, Tile.WALL)
            # If we hit a wall, we can remove the space with the the wall from
            # the set of unexplored spaces.
            self._remove_from_frontier(self.last_move)
        elif v == Output.MOVED:
            # We moved to an empty space.
            self.position = self.last_move
            self.map_.set_tile(self.position, Tile.EMPTY)
            self._remove_from_frontier(self.last_move)
            for p in points_around(self.last_move):
                self._add_to_frontier(p)
        elif v == Output.OXYGEN:
            # We moved and found the oxygen system.
            self.position = self.last_move
            self.map_.set_tile(self.position, Tile.OXYGEN)
            self._remove_from_frontier(self.last_move)
            for p in points_around(self.last_move):
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

def flood_fill(grid, start_pos, cb=None, log=None):
    # The -1 here seems weird, but we "fill" the start position with OXYGEN
    # on the first pass through the loop below, which is incorrect since we
    # assume the start position starts with OXYGEN. Hence the -1.
    fill_time = -1
    frontier = set([start_pos])
    while frontier:
        if log:
            log(f"[flood_fill] Time step = {fill_time}, frontier = {frontier}.")
        next_frontier = set()
        for p in frontier:
            grid.set_tile(p, Tile.OXYGEN)
            for q in points_around(p):
                tile = grid.get_tile(q)
                # We can't fill WALLs, and we can skip any tile that already
                # has OXYGEN.
                if tile != Tile.WALL and tile != Tile.OXYGEN:
                    next_frontier.add(q)
        cb(frontier)
        fill_time += 1
        frontier = next_frontier
    return fill_time

def curses_main(stdscr): 
    pad_width = 50
    pad_height = 50
    pad = curses.newpad(pad_height, pad_width)

    # Put a box around the pad border so we can see where it is in our
    # "window".
    pad.box()

    # Seed random so that we always get the same sequence of random choices
    # for the robot.
    random.seed(0)

    tx = pad_width // 2
    ty = pad_height // 2

    # The last known position of the robot, in "screen coordinates".
    last_pos = Point(tx, ty)

    # The position of the oxygen system, in "screen coordinates".
    oxygen_pos = None

    def refresh_pad(pad):
        width = min(pad_width, curses.COLS - 1)
        height = min(pad_height, curses.LINES - 1)
        pad.refresh(0, 0, 0, 0, height, width)

    def on_move(pos, last_move, result):
        nonlocal last_pos, oxygen_pos

        # Translate from map to screen coordinates.
        pos = pos.translate(tx, ty)
        last_move = last_move.translate(tx, ty)

        if result == Output.WALL:
            pad.addch(last_move.y, last_move.x, '#')
        elif result == Output.OXYGEN:
            # Save position of oxygen system for later use (we'll draw it on
            # the map when the robot moves off of this space).
            oxygen_pos = pos

        # Fix up old robot position.
        if last_pos != Point(tx, ty):
            c = '.'
            if oxygen_pos and last_pos == oxygen_pos:
                c = 'O'
            pad.addch(last_pos.y, last_pos.x, c)
        else:
            pad.addch(ty, tx, '<')

        # draw robot in new position
        pad.addch(pos.y, pos.x, '@')

        last_pos = pos

        # Draw pad in our "window".
        #
        # TODO: center pad in window if it's smaller
        refresh_pad(pad)

    # TODO: show log messages in curses interface
    log_file = open("run.log", "w")
    def log(msg):
        print(msg, file=log_file)

    program = intcode.read_initial_memory("input")
    r = Robot(program, on_move=on_move, log_fn=log)
    r.run()
    
    # After the robot halts, we should have the whole map in its "memory".
    # Use it to get the shortest path from the start position to the oxygen
    # system.
    best_path = bfs(Point(0, 0), oxygen_pos.translate(-tx, -ty), r.map_)

    # Color the best path in the curses display.
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    for p in best_path:
        p = p.translate(tx, ty)
        c = '.'
        if p == Point(tx, ty):
            c = '>'
        elif p == oxygen_pos:
            c = 'O'
        pad.addch(p.y, p.x, c, curses.color_pair(1))
    refresh_pad(pad)
    pad.getch()

    # In part 2, we need to figure out how long it takes for the oxgygen to
    # fill the space after the robot repairs the oxygen system. The oxygen
    # fills all adjacent squares at each time step, so the time taken is just
    # the shortest path to the square farthest away from the oxygen system.
    # For fun let's animate "filling" all the squares on the map.
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    def fill_cb(filled_spaces):
        for p in filled_spaces:
            # This point filled up with oxygen on this time step.
            p = p.translate(tx, ty)
            pad.addch(p.y, p.x, 'O', curses.color_pair(2))
        refresh_pad(pad)
        time.sleep(0.125)
    fill_time = flood_fill(r.map_, oxygen_pos.translate(-tx, -ty), fill_cb, log)
    pad.getch()

    # Maybe stop and wait for a keypress here?
    # time.sleep(5)

    # Extra a character from the pad, handling the ALT_CHARSET crap.
    def get_char(x, y):
        c = pad.inch(y, x)
        # log(f"[get_char] x = {x}, y = {y}, c = {hex(c)}.")
        if c & curses.A_ALTCHARSET:
            if c == curses.ACS_ULCORNER:
                return u"\u250c"
            elif c == curses.ACS_HLINE:
                return u"\u2500"
            elif c == curses.ACS_URCORNER:
                return u"\u2510"
            elif c == curses.ACS_VLINE:
                return u"\u2502"
            elif c == curses.ACS_LLCORNER:
                return u"\u2514"
            elif c == curses.ACS_LRCORNER:
                return u"\u2518"
            return ''
        return chr(c & ~curses.A_ATTRIBUTES)

    # Capture pad contents.
    pad_contents = ""
    for row in range(0, pad_height):
        for col in range(0, pad_width):
            pad_contents += get_char(col, row)
        pad_contents += "\n"

    return best_path, pad_contents, fill_time


def flood_fill_test():
    def parse_map(s):
        map_ = Map()
        y = 0
        for line in s:
            print(f"Got line: {line}")
            x = 0
            for c in line:
                print(f"Got character: {c}")
                p = Point(x, y)
                if c == '#':
                    print(f"Got WALL at {p}")
                    map_.set_tile(p, Tile.WALL)
                elif c == ".":
                    print(f"Got EMPTY at {p}")
                    map_.set_tile(p, Tile.EMPTY)
                elif c == "O":
                    print(f"Got OXYGEN at {p}")
                    map_.set_tile(p, Tile.OXYGEN)
                x += 1
            y += 1
        return map_

    example_map = [
        " ##   ",
        "#..## ",
        "#.#..#",
        "#.O.# ",
        " ###  ",
    ]
    map_ = parse_map(example_map)
    print(f"Got map: {map_}")
    fill_time = flood_fill(map_, Point(2, 3))
    print(f"Map filled in {fill_time} time steps.")

if __name__ == "__main__":
    best_path, pad_contents, fill_time = curses.wrapper(curses_main)
    print(pad_contents)
    print(f"Thanks for playing! Best path to oxygen system is "
          f"{len(best_path) - 1} moves long. It took {fill_time} time steps "
          f"to fill the entire map with oxygen.")
    print("Be seeing you...")

