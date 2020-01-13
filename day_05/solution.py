# Fix up sys.path so we can find intcode. Python imports suck.
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import intcode

if __name__ == '__main__':
    memory = intcode.read_initial_memory("input")
    # For this exercise the program itself outputs the result using the OUTPUT
    # opcode.
    intcode.intcode_run(memory)
