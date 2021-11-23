#!/usr/bin/env python3

import numpy as np
import re

class LightGrid:
    def __init__(self, width, height):
        self.array = np.zeros((width, height), dtype='uint16')

    def _index(self, x0, y0, x1, y1):
        return (slice(x0, x1+1), slice(y0, y1 + 1))

    def turn_on(self, x0, y0, x1, y1):
        self.array[self._index(x0, y0, x1, y1)] = 1

    def turn_off(self, x0, y0, x1, y1):
        self.array[self._index(x0, y0, x1, y1)] = 0

    def toggle(self, x0, y0, x1, y1):
        indices = self._index(x0, y0, x1, y1)
        self.array[indices] = 1 - self.array[indices]

    def increase_brightness(self, x0, y0, x1, y1, c=1):
        # NOTE: we're assuming we'll never overflow here
        self.array[self._index(x0, y0, x1, y1)] += c

    def decrease_brightness(self, x0, y0, x1, y1):
        a = self.array[self._index(x0, y0, x1, y1)]
        a[a>0] -= 1

    def count_on(self):
        return np.sum(self.array)

def apply_instructions(light_grid, fns):
    with open("input.txt") as input_file:
        prog = re.compile("(turn on|turn off|toggle) ([\d]+),([\d]+) through ([\d]+),([\d]+)")
        for line in input_file:
            # print(line)
            m = prog.match(line)
            if not m:
                raise ValueError(f"Invalid input format: {line}")

            inst = m.group(1)
            x0, y0, x1, y1 = [int(x) for x in m.group(2, 3, 4, 5)]
            print(f"{inst} ({x0}, {y0}) to ({x1}, {y1}).")
            fns[inst](x0, y0, x1, y1)

def main():
    light_grid = LightGrid(width=1000, height=1000)
    apply_instructions(light_grid, {
        "turn on": lambda x0, y0, x1, y1: light_grid.turn_on(x0, y0, x1, y1),
        "turn off": lambda x0, y0, x1, y1: light_grid.turn_off(x0, y0, x1, y1),
        "toggle": lambda x0, y0, x1, y1: light_grid.toggle(x0, y0, x1, y1),
    })   
    print(f"There are {light_grid.count_on()} lights on in part 1.")

    light_grid = LightGrid(width=1000, height=1000)
    apply_instructions(light_grid, {
        "turn on": lambda x0, y0, x1, y1: light_grid.increase_brightness(x0, y0, x1, y1),
        "turn off": lambda x0, y0, x1, y1: light_grid.decrease_brightness(x0, y0, x1, y1),
        "toggle": lambda x0, y0, x1, y1: light_grid.increase_brightness(x0, y0, x1, y1, 2),
    })   
    print(f"The total brightness is {light_grid.count_on()} in part 2.")

    

if __name__ == "__main__":
    main()
