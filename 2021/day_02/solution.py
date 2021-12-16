#!/usr/bin/env python3

import re

class Sub1:
    def __init__(self):
        self.x = 0
        self.depth = 0
    
    def forward(self, n):
        self.x += n

    def down(self, n):
        self.depth += n

    def up(self, n):
        self.depth -= n

class Sub2:
    def __init__(self):
        self.x = 0
        self.depth = 0
        self.aim = 0
        
    def forward(self, n):
        self.x += n
        self.depth += n * self.aim

    def down(self, n):
        self.aim += n

    def up(self, n):
        self.aim -= n

def solve(sub, cmds):
    prog = re.compile("(forward|down|up) (\d+)")
    for c in cmds:
        m = prog.match(c)
        cmd = m.group(1)
        n = int(m.group(2))
        if cmd == "forward":
            print(f"Forward {n}")
            sub.forward(n)
        elif cmd  == "down":
            print(f"Down {n}")
            sub.down(n)
        elif cmd == "up":
            print(f"Up {n}")
            sub.up(n)
    print(f"Horizontal position: {sub.x}, depth: {sub.depth}, product: {sub.x * sub.depth}")    

def main():
    # Test commands.
    # cmds = [
    #     "forward 5",
    #     "down 5",
    #     "forward 8",
    #     "up 3",
    #     "down 8",
    #     "forward 2",
    # ]
    with open("input.txt") as input_file:
        solve(Sub1(), input_file)

    with open("input.txt") as input_file:
        solve(Sub2(), input_file)

if __name__ == "__main__":
    main()
