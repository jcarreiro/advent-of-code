#!/usr/bin/env python3

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

def read_directions():
    with open("input.txt") as input_file:
        # The input is one giant line; we read it one char at a time.
        for direction in input_file.readline().strip():
            # print(f"Got direction: {direction}")
            if direction == ">":
                yield Point(1, 0)
            elif direction == "v":
                yield Point(0, -1)
            elif direction == "<":
                yield Point(-1, 0)
            elif direction == "^":
                yield Point(0, 1)
            else:
                raise ValueError(f"Unrecognized direction: {direction}.")

def main():
    def move(whom, pos, direction, visited):
        new_pos = pos + direction
        # print(f"{whom} moved from {pos} to {new_pos}.")
        visited.add(new_pos)
        return new_pos

    # Part 1: Only Santa visits the houses.
    visited = set()
    santa_pos = Point(0, 0)
    visited.add(santa_pos)
    for d in read_directions():
        santa_pos = move("Santa", santa_pos, d, visited)
    print(f"Visited {len(visited)} houses in part 1.")

    # Part 2: Santa and Robo-Santa alternate following the directions.
    santa_pos = Point(0, 0)
    robot_pos = Point(0, 0)
    i = 0
    visited.clear()
    visited.add(santa_pos)
    for d in read_directions():
        if i % 2 == 0:
            santa_pos = move("Santa", santa_pos, d, visited)
        else:
            robot_pos = move("Robo-Santa", robot_pos, d, visited)
        i += 1
    print(f"Visited {len(visited)} houses in part 2.")

if __name__ == "__main__":
    main()
