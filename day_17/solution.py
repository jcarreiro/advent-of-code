#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import curses
import intcode
import random

from enum import Enum, IntEnum, auto

# Mostly the same as day 15, bleh.
class Tile(Enum):
    SCAFFOLD = auto()
    EMPTY = auto()
    UNKNOWN = auto()

class Direction(Enum):
    NORTH = auto()
    SOUTH = auto()
    WEST = auto()
    EAST = auto()

class Output(IntEnum):
    SCAFFOLD = 35 # '#'
    EMPTY = 46    # '.'
    NEWLINE = 10  # '\n's

def curses_main(stdscr):
    pad_width = 75
    pad_height = 75
    pad = curses.newpad(pad_height, pad_width)

    # Put a box around the pad border so we can see where it is in our
    # "window".
    pad.box()

    # Seed random so that we always get the same sequence of random choices
    # for the robot.
    random.seed(0)

    def refresh_pad(pad):
        width = min(pad_width, curses.COLS - 1)
        height = min(pad_height, curses.LINES - 1)
        pad.refresh(0, 0, 0, 0, height, width)

    log_file = open("run.log", "w")

    x = 1
    y = 1
    def output(v):
        nonlocal x, y
        print(f"Got output {str(v)} at x={x}, y={y}.", file=log_file)
        if v == Output.SCAFFOLD:
            pad.addch(y, x, '#')
            x += 1
        elif v == Output.EMPTY:
            pad.addch(y, x, '.')
            x += 1
        elif v == Output.NEWLINE:
            y += 1
            x = 1
        refresh_pad(pad)

    program = intcode.read_initial_memory("input")
    im = intcode.IntcodeMachine(program, output_fn=output)
    im.run()

    # wait for keypress before exiting
    pad.getch()

    # Get a character from the pad, handling the ALT_CHARSET crap.
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

    # Now that we have the pad contents, compute the "alignment parameters".
    # The pad isn't that big, we can just loop over all characters to get the
    # intersections.
    total = 0
    for row in range(0, pad_height):
        for col in range(0, pad_width):
            c = get_char(col, row)
            if c == "#":
                neighbors = [
                    (col,     row - 1), # N
                    (col + 1, row    ), # E
                    (col,     row + 1), # S
                    (col - 1, row    ), # W
                ]
                intersection = True
                for n in neighbors:
                    if get_char(n[0], n[1]) != "#":
                        intersection = False
                if intersection:
                    # Note that we offset all of the coordinates to draw the
                    # border...
                    total += (row - 1) * (col - 1)
                    pad.addch(row, col, "O")
    refresh_pad(pad)
    pad.getch()

    # Capture pad contents.
    pad_contents = ""
    for row in range(0, pad_height):
        for col in range(0, pad_width):
            pad_contents += get_char(col, row)
        pad_contents += "\n"

    return pad_contents, total

if __name__ == "__main__":
    pad_contents, total = curses.wrapper(curses_main)
    print(pad_contents)
    print(f"Sum of alignment parameters was {total}.")
    print("Be seeing you...")
