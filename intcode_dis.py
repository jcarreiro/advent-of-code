#!/usr/bin/env python3
#
# Simple disassembler for intcode programs.

import argparse
import intcode
import os
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('program', type=str, help='Path to program')
    args = parser.parse_args()

    prog = intcode.read_initial_memory(args.program)
    pc = 0
    im = intcode.IntcodeMachine(prog[:])
    while pc < len(prog):
        pc, inst = im.decode(pc, prog)
        print(f"{pc:04x} {inst}")
