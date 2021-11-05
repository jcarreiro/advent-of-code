import cProfile
import datetime
import io
import math
import matplotlib.pyplot as plt
import numpy as np
import pstats
import time

from mpl_toolkits.mplot3d import Axes3D

def print_position_and_velocity(step, positions, velocities):
    print(f"After {step} steps:")
    for i in range(positions.shape[0]):
        px, py, pz = positions[i]
        vx, vy, vz = velocities[i]
        print(
            f"pos=<x={px:3}, y={py:3}, z={pz:3}>, vel=<x={vx:3}, y={vy:3}, z={vz:3}>")
    return False  # never stop simulation early

# Call a list of callbacks. If this method returns True, the simulation should stop early.
def call_callbacks(callbacks, step, positions, velocities):
    for cb in callbacks:
        if cb(step, positions, velocities):
            return True
    return False

# Simulate for max_steps steps.
#
# At a high level, this method:
#
#   1. Computes the gravity vector for each object from the sign of the distance
#      from that objecct to all other objects (yes, that's how gravity works for
#      this problem).
#
#   2. Updates the velocity vector for each object using the gravity vector.
#
#   3. Updates the position vector for each object using the velocity vector.
#
# positions and velocities are expected to be Mx3 matrices, where M is the number
# of objects in the simulation.
def simulate(positions, velocities, max_steps, callbacks=None):
    step = 0
    while step < max_steps:
        if call_callbacks(callbacks, step, positions, velocities):
            break
        for i in range(positions.shape[0]):
            g = np.sum(np.sign(positions - positions[i]), axis=0)
            velocities[i] += g
        positions += velocities
        step += 1
    return (step, positions, velocities)

def simulate2(positions, velocities, max_steps, callbacks=None):
    step = 0
    while step < max_steps:
        if call_callbacks(callbacks, step, positions, velocities):
            break
        velocities += np.sum(np.sign(positions[None,:] - positions[:,None]), axis=1)
        positions += velocities
        step += 1
    return (step, positions, velocities)

# Simulate on one axis. Assumes x, v_x are 1D arrays.
def simulate_one_axis(x, v_x, max_steps, callbacks=None):
    for step in range(1, int(max_steps) + 1):
        v_x += np.sum(np.sign(np.subtract.outer(x, x)), axis=0)
        x += v_x
        if call_callbacks(callbacks, step, x, v_x):
            break
    return (step, x, v_x)

# First test case from problem:
#   <x=-1, y=0, z=2>
#   <x=2, y=-10, z=-7>
#   <x=4, y=-8, z=8>
#   <x=3, y=5, z=-1>

# Second test case from problem:
#   <x=-8, y=-10, z=0>
#   <x=5, y=5, z=10>
#   <x=2, y=-7, z=3>
#   <x=9, y=-8, z=-3>

# This was the actual puzzle input:
#   <x=9, y=13, z=-8>
#   <x=-3, y=16, z=-17>
#   <x=-4, y=11, z=-10>
#   <x=0, y=-2, z=-2>

def solve_part1(positions, velocities):
    max_steps = 1000
    simulate(positions, velocities, max_steps)

    print_position_and_velocity(max_steps, positions, velocities)

    potential_energy = np.sum(np.abs(positions), axis=1)
    kinetic_energy = np.sum(np.abs(velocities), axis=1)
    energy = potential_energy * kinetic_energy

    print(f"Energy after {max_steps} steps:")
    for i in range(positions.shape[0]):
        px, py, pz = np.abs(positions[i])
        kx, ky, kz = np.abs(velocities[i])
        print(f"pot: {px:3} + {py:3} + {pz:3} = {potential_energy[i]:3}; "
              f"kin: {kx:3} + {ky:3} + {kz:3} = {kinetic_energy[i]:3}; "
              f"total: {potential_energy[i]:3} * {kinetic_energy[i]:3} "
              f"= {energy[i]:3}")
    print(f"Sum of total energy:", end="")
    for i in range(energy.shape[0]):
        if i != 0:
            print(" +", end="")
        print(f" {energy[i]:3}", end="")
    print(f" = {np.sum(energy):5}")

def solve_part2(fn, positions, velocities, max_steps):
    # Let's make the unjustified assumption that initial state will repeat (as
    # oppposed to some later state). Then, since all the axes are independent,
    # we can solve the problem by finding the period of the cycle for each axis
    # separately -- then the period of the cycle for the entire system will be
    # the lcm of the periods for each axis.
    def find_cycle(axis_label, x, v, max_steps):
        x0 = x.copy()
        v0 = v.copy()
        t0 = time.monotonic()

        def print_progress(step, positions, velocities):
            if step % 1000 == 0:
                delta = time.monotonic() - t0
                pct_done = float(step)/float(max_steps)
                rate = float(step)/float(delta)
                eta = 'inf'
                if rate:
                    eta = datetime.timedelta(
                        seconds=float(max_steps - step) / rate)
                print(f"{step:06}/{max_steps} ({pct_done:0.2%}), {rate:0.2} steps / s, elapsed {datetime.timedelta(seconds=delta)}, eta {eta}.")

        def check_for_repeat_of_initial_state(_, x, v):
            return np.all(np.equal(x, x0)) and np.all(np.equal(v, v0))

        step, x, v = simulate_one_axis(x, v, max_steps, [print_progress, check_for_repeat_of_initial_state])
        if step < max_steps or check_for_repeat_of_initial_state(0, x, v):
            print(f"Found cycle on {axis_label} axis after {step} steps.")
            print(f"{axis_label}0 = {x0}, v0 = {v0}, {axis_label} = {x}, v = {v}")
            return step
        else:
            print(f"No cycle found on {axis_label} axis, giving up!")
            return None

    x, y, z = positions.T
    v_x, v_y, v_z = velocities.T

    # Check for cycle on x axis.
    x_period = find_cycle("x", x, v_x, max_steps)
    if not x_period:
        return

    # Check for cycle on y axis.
    y_period = find_cycle("y", y, v_y, max_steps)
    if not y_period:
        return

    # Check for cycle on z axis.
    z_period = find_cycle("z", z, v_z, max_steps)
    if not z_period:
        return

    period = math.lcm(x_period, y_period, z_period)
    print(f"Solution repeats with period {period}.")

def profile_simulation(fn, positions, velocities, max_steps):
    # Profile code for part 2, to see if we can speed up the simulation.
    pr = cProfile.Profile()
    pr.enable()

    fn(positions, velocities, max_steps)

    # Stop profiling and print stats.
    pr.disable()
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

def compare_results(positions, velocities, max_steps):
    p0 = positions.copy()
    p1 = positions.copy()
    v0 = velocities.copy()
    v1 = velocities.copy()
    for step in range(1, int(max_steps + 1)):
        _, p0, v0 = simulate(p0, v0, 1)
        _, p1, v1 = simulate2(p1, v1, 1)
        if not (np.all(np.equal(p0, p1)) and np.all(np.equal(v0, v1))):
            print(f"Simulation diverged at timestep {step}.\np0 =\n{p0}\nv0 =\n{v0}\np1 =\n{p1}\nv1 =\n{v1}")
            break
    if step == max_steps:
        print(f"Simulations did not diverge in {step} timesteps.")

if __name__ == "__main__":
    # In part 1, we just have to simulate the system for 1000 time steps, then
    # print the total energy.
    #
    # positions = np.array([
    #     [ 9,  13,  -8],
    #     [-3,  16, -17],
    #     [-4,  11, -10],
    #     [ 0,  -2,  -2],
    # ], dtype=np.int16)
    # velocities = np.zeros((4,3), dtype=np.int16)
    # solve_part1(positions, velocities)

    # In part 2, we have to find the period before the system repeats a previous
    # state.
    #
    # This is the example from the problem, which has a cycle of length 2772 (the
    # initial state repeats after that many time steps).
    #
    # positions = np.array([
    #     [-1,   0,  2],
    #     [2, -10, -7],
    #     [4,  -8,  8],
    #     [3,   5, -1],
    # ], dtype=np.int16)

    # This is the second example from the problem. This initial state "takes
    # 4686774924 steps before it repeats a previous state" (whether it repeats
    # the initial state or another state is not specified).
    #
    # If we need to store the entire history to find the repeat, then we'd need
    #
    #   4 bytes / value * 24 values / step * 4686774924 steps ~= 450 GB
    #
    # Which seems ridiculous, so I assume we don't need to store and check the
    # entire history to find the repeat. So let's check to see if the initial
    # state repeats in 4686774924 steps, I guess.
    #
    # Note that since the axes are independent, there's a fast way to find the
    # period of the cycle; see the solve_part2() method above.
    #
    #  positions = np.array([
    #    [-8, -10,  0],
    #    [ 5,   5, 10],
    #    [ 2,  -7,  3],
    #    [ 9,  -8, -3],
    # ], dtype=np.int16)

    # This is the actual problem input.
    positions = np.array([
        [ 9,  13,  -8],
        [-3,  16, -17],
        [-4,  11, -10],
        [ 0,  -2,  -2],
    ], dtype=np.int16)

    velocities = np.zeros((4, 3), dtype=np.int16)
    solve_part2(simulate2, positions, velocities, 5e9)
