#!/usr/bin/env python3

from enum import IntEnum

class Opcode(IntEnum):
    ADD = 1
    MULTIPLY = 2
    HALT = 99

# Runs an intcode program; memory is the starting memory contents. Returns the
# value at address 0 once the program halts (this is the program's output).
def intcode_run(memory):
    # Each instruction is 4 integers long: (opcode, src_addr1, src_addr2,
    # dest_addr).
    pc = 0
    while True:
        print(f"[{pc:04x}] ({', '.join([str(x) for x in memory[pc:pc+4]])})")

        opcode = memory[pc]
        if opcode == Opcode.ADD:
            s1, s2, d = memory[pc+1:pc+4]
            memory[d] = memory[s1] + memory[s2]
        elif opcode == Opcode.MULTIPLY:
            s1, s2, d = memory[pc+1:pc+4]
            memory[d] = memory[s1] * memory[s2]
        elif opcode == Opcode.HALT:
            break
        else:
            raise ValueError(f"Invalid opcode: {opcode}")

        pc += 4  # all instructions are 4 bytes long
    # Result of program is in memory[0]
    return memory[0]

# For part 1, we just need to run the program and get the output.
def solve_part1():
    # read initial contents of memory
    with open("input") as f:
        memory = [int(x) for x in f.readline().split(',')]
    # "before running the program, replace position 1 with the value 12 and
    # replace position 2 with the value 2"
    memory[1] = 12
    memory[2] = 2
    output = intcode_run(memory)
    print(f"The value at position 0 is {output}.")

# For part 2, we need to run the same program as part 1, but now we need to
# find the pair of inputs (the initial values at addresses 1 and 2) that give
# us the output 19690720.
def solve_part2():
    # read initial contents of memory
    with open("input") as f:
        initial_memory = [int(x) for x in f.readline().split(',')]

    # I don't know of any faster way to do this than the obvious search.
    # The problem definition gives bounds of [0, 99] for the two unknown
    # inputs.
    for n in range(0, 100):
        output = None
        for v in range(0, 100):
            print(f"Trying ({n}, {v}).")
            # Note that a shallow copy is fine here since the list just
            # contains values (ints).
            memory = initial_memory[:]
            memory[1] = n
            memory[2] = v
            output = intcode_run(memory)
            print(f"Got output {output}.")
            if output == 19690720:
                break
        if output == 19690720:
            break

if __name__ == "__main__":
    solve_part1()
    solve_part2()
