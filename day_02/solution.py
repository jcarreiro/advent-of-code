#!/usr/bin/env python3

from enum import IntEnum

class Opcode(IntEnum):
    ADD = 1
    MULTIPLY = 2
    HALT = 99

def solve(memory):
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

if __name__ == "__main__":
    # read initial contents of memory
    with open("input") as f:
        memory = [int(x) for x in f.readline().split(',')]
    # "before running the program, replace position 1 with the value 12 and
    # replace position 2 with the value 2"
    memory[1] = 12
    memory[2] = 2
    output = solve(memory)
    print(f"The value at position 0 is {output}.")
