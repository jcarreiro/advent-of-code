#!/usr/bin/env python3

import argparse
import itertools
import numpy as np
import re

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

class Rect:
    def __init__(self, top, left, bottom, right):
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right

    def __repr__(self):
        return f"Rect({self.top}, {self.left}, {self.bottom}, {self.right})"

    def contains(self, p):
        return self.left <= p.x and p.x <= self.right and self.bottom <= p.y and p.y <= self.top

def simulate(vx, vy, max_timestep=10, callback=None):
    p = Point(0, 0)
    trajectory = []
    for t in range(0, max_timestep):
        trajectory.append(p)
        
        print(f"[{t}] position = ({p.x}, {p.y}), velocity = ({vx}, {vy})")
        
        if callback and callback(t, p):
            print("Ending simulation!")
            break
        
        # Update position.
        p = Point(p.x + vx, p.y + vy)

        # Update velocity.
        #
        # Drag reduces our horizontal velocity, to a minimum of 0.
        vx = max(vx - 1, 0)
        
        # Gravity reduces our vertical velocity.
        vy -= 1
        
    return trajectory

def print_trajectory(trajectory, target_area):
    max_x = max([p.x for p in trajectory] + [target_area.right])
    max_y = max([p.y for p in trajectory] + [target_area.top])
    min_x = min([p.x for p in trajectory] + [target_area.left])
    min_y = min([p.y for p in trajectory] + [target_area.bottom])
    for y in range(max_y, min_y - 1, -1):
        print(f"{y:3} ", end="")
        for x in range(min_x, max_x + 1):
            if x == 0 and y == 0:
                print("S", end="")
            elif Point(x, y) in trajectory:
                print("#", end="")
            elif target_area.contains(Point(x, y)):
                print("T", end="")
            else:
                print(".", end="")
        print()
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-timestep", type=int, default=20)
    parser.add_argument("--velocity", type=str)
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()

    # In this problem, we are given a target area (e.g. x=[20, 30], y=[10, -5])
    # and we need to find the trajectory, starting from the origin, that results
    # in our probe reaching the maximum possible height before ending up in the
    # target area at the end of any time step.
    #
    # Our probe's is affected by drag which reduces its velocity on the x axis
    # by 1 per time step, to a minimum of 0, and by gravity, which reduces its
    # velocity on the y axis by 1 per time step, no minimum.
    #
    # Get the target area.
    m = re.match(
        "target area: x=(-?\d+)..(-?\d+), y=(-?\d+)..(-?\d+)",
        args.input_file.readline(),
    )
    target = Rect(
        top=int(m[4]),
        left=int(m[1]),
        bottom=int(m[3]),
        right=int(m[2]),
    )
    print(f"Got target area: {target}")

    def stop_if_passed_target(t, p):
        return target.contains(p) or p.x > target.right or p.y < target.bottom

    # This was an initial test to make sure I could recreate the example from
    # the puzzle:
    #
    #   trajectory = simulate(7, 2, args.max_timestep, stop_if_passed_target)
    #   print_trajectory(trajectory, target)
    #
    # For the actual puzzle, we were asked to hit a target area of:
    #
    #   x = [236, 262], y = [-78, -58]
    #
    # Clearly the best we can do on the y axis is an initial velocity of +77; we
    # will pass back through y=0 with a velocity of v_y = -77 (by symmetry) and
    # just hit the target area, after reaching a height of 77 + 76 + ... + 1 =
    # 77 * 78 / 2 = 3003.
    #
    # This trajectory takes 156 time steps to reach the target (77 * 2 + 2), so
    # the only remaining question is, is there a value for v_x that hits the
    # target area after 156 time steps? This is actually easy since, due to drag,
    # our v_x will become 0 after v_x(0) time steps; therefore we can simply
    # compute:
    #
    #   x(t) = x_0 + vt + 1/2 at^2
    #    236 = vt - 1/2 t^2         (a = -1)
    #    236 = t^2 - t^2/2          (assume v = t since v(t) = 0 after t steps)
    #    236 = t^2 / 2
    #     t ~= 22
    #
    # So a v_x(0) of ~22 will reach the target area after 22 steps, and remain
    # there.

    def hit_target(trajectory, target):
        return next(filter(target.contains, trajectory), False)

    def max_y(trajectory):
        return max([p.y for p in trajectory])

    if args.velocity:
        # Run a single trajectory; this is useful for testing.
        vx, vy = [int(x) for x in args.velocity.split(",")]
        print(f"Simulating {vx}, {vy}.")
        trajectory = simulate(vx, vy, args.max_timestep, stop_if_passed_target)
        print_trajectory(trajectory, target)
        if hit_target(trajectory, target):
            print(f"Hit target!")
        print(f"Max y was {max_y(trajectory)}.")
    else:    
        # Compute optimal velocity on each axis.
        #
        # For now let's just do a simple grid search. We'll distribute a number of
        # points uniformly over a range of initial velocities and report the best
        # one we find.
        #
        # We can cut down on the search space a bit. For example, any vx less than
        # 1/2 of the distance to the target will result in the probe never reaching
        # the target.
        vxs = np.arange(0, 10)
        vys = np.arange(0, 10)
        max_y = -np.inf
        for (vx, vy) in itertools.product(vxs, vys):
            print(f"Checking {vx}, {vy}")
            trajectory = simulate(vx, vy, args.max_timestep, stop_if_passed_target)
            # print_trajectory(trajectory, target)
    
            # Check if we hit the target.
            if next(filter(target.contains, trajectory), False):
                # Save the max y we hit, if we hit the target.
                y = max([p.y for p in trajectory])
                if y > max_y:
                    max_y = y
        print(f"Max y was {max_y}.")

if __name__ == "__main__":
    main()
