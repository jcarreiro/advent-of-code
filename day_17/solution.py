#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import curses
import curses.ascii
import intcode
import random

from common import Point
from enum import Enum, IntEnum, auto

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

    def log(msg):
        print(msg, file=log_file)

    x = 1
    y = 1
    last_output = None
    total_dust = 0

    def output_fn(v):
        nonlocal x, y, last_output, total_dust

        log(f"[output] Got output {v} ('{curses.ascii.unctrl(chr(v))}') at x={x}, y={y}.")

        # If we get a non-ASCII value, it's our score.
        if v > 127:
            total_dust = v
        else:
            c = chr(v)
            if c == "\n":
                if last_output == "\n":
                    y = 1
                    x = 1
                else:
                    y += 1
                    x = 1
            else:
                pad.addch(y, x, c)
                refresh_pad(pad)
                x += 1
            last_output = c

    class InputState(Enum):
        INPUT_MAIN = auto()
        INPUT_A = auto()
        INPUT_B = auto()
        INPUT_C = auto()
        INPUT_VIDEO = auto()
        INPUT_DONE = auto()

    # "Compile" a movement routine into a list of "ASCII codes".
    def compile(prog):
        l = [ord(x) for x in prog] + [ord("\n")]
        # Reverse since we want to pop() instructions off to return them from
        # input_fn, below.
        l.reverse()
        return l

    def get_next_move(prog, state, next_state):
        v = prog.pop()
        s = state if v != ord("\n") else next_state
        return (v, s)

    input_state = InputState.INPUT_MAIN
    move_main = compile("A")
    move_a = compile("R,2")
    move_b = compile("R,2")
    move_c = compile("R,2")
    want_video = compile("y")

    def input_fn(_):
        nonlocal input_state

        table = {
            InputState.INPUT_MAIN: (
                move_main,
                InputState.INPUT_A,
            ),
            InputState.INPUT_A: (
                move_a,
                InputState.INPUT_B,
            ),
            InputState.INPUT_B: (
                move_b,
                InputState.INPUT_C,
            ),
            InputState.INPUT_C: (
                move_c,
                InputState.INPUT_VIDEO,
            ),
            InputState.INPUT_VIDEO: (
                want_video,
                InputState.INPUT_DONE,
            ),
        }
        prog, next_state = table[input_state]
        next_move, input_state = get_next_move(prog, input_state, next_state)
        log(f"[input] Returning move {next_move}, next state is {input_state}.")
        return next_move

    program = intcode.read_initial_memory("input")
    program[0] = 2 # "wake up" the robot
    im = intcode.IntcodeMachine(
        program,
        output_fn=output_fn,
        input_fn=input_fn,
    )
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
    #
    # This was only needed for part 1.
    # total = 0
    # for row in range(0, pad_height):
    #     for col in range(0, pad_width):
    #         c = get_char(col, row)
    #         if c == "#":
    #             neighbors = [
    #                 (col,     row - 1), # N
    #                 (col + 1, row    ), # E
    #                 (col,     row + 1), # S
    #                 (col - 1, row    ), # W
    #             ]
    #             intersection = True
    #             for n in neighbors:
    #                 if get_char(n[0], n[1]) != "#":
    #                     intersection = False
    #             if intersection:
    #                 # Note that we offset all of the coordinates to draw the
    #                 # border...
    #                 total += (row - 1) * (col - 1)
    #                 pad.addch(row, col, "O")
    # refresh_pad(pad)
    # pad.getch()

    # Now to solve part 2, we need to find a path that visits all points on the
    # scaffold, and which we can express as a "movement routine" composed of
    # three "movement functions" we define ("A", "B", and "C"; for example
    # "A,B,C"). Each movement function can be composed of three insructions:
    # turn left ("L"), turn right ("R"), or a number to indicate the robot
    # should move forward N units in the direction it is currently facing (e.g.
    # "L,2,R,8"). Finally each of these routines, including the main routine,
    # can be at most 20 characters (not counting the terminating newline).
    #
    # Let's start by finding a path that visits every point on the scaffold,
    # then we can try to figure out how to break that down into a program that
    # fits in our constraints (and if that's not possible, we'll backout and
    # find a different path, I guess).
    #
    # Since we don't care if the path is short (we just need a short enough
    # program) we can use a greedy approach.

    # Capture pad contents.
    pad_contents = ""
    for row in range(0, pad_height):
        for col in range(0, pad_width):
            pad_contents += get_char(col, row)
        pad_contents += "\n"

    return pad_contents, total_dust

if __name__ == "__main__":
    pad_contents, total_dust = curses.wrapper(curses_main)
    print(pad_contents)
    print(f"Collected {total_dust} dust.")
    print("Be seeing you...")
