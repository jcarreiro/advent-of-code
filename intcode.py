from collections import namedtuple
from enum import IntEnum

class Opcode(IntEnum):
    ADD = 1
    MULTIPLY = 2
    INPUT = 3
    OUTPUT = 4
    JT = 5
    JF = 6
    LT = 7
    EQ = 8
    HALT = 99

class ParameterMode(IntEnum):
    POSITION = 0
    IMMEDIATE = 1

Op = namedtuple('Op', ['param_count'])

ops = {
    Opcode.ADD: Op(3),
    Opcode.MULTIPLY: Op(3),
    Opcode.INPUT: Op(1), # NB. parameter can never be IMMEDIATE
    Opcode.OUTPUT: Op(1),
    Opcode.JT: Op(2),
    Opcode.JF: Op(2),
    Opcode.LT: Op(3),
    Opcode.EQ: Op(3),
    Opcode.HALT: Op(0),
}

class Parameter:
    def __init__(self, mode, value):
        self.mode = mode
        self.value = value

    def load(self, memory):
        if self.mode == ParameterMode.IMMEDIATE:
            return self.value
        return memory[self.value]

class Instruction:
    def __init__(self, opcode, params):
        self.opcode = opcode
        self.params = params

    def __str__(self):
        s = "".join([str(p.mode) for p in self.params]) + f"{self.opcode:02}"
        if self.params:
            s = s + "," + ",".join([str(p.value) for p in self.params])
        return s

# Decode a single instruction; returns it and the new value of the pc.
def decode(memory, pc):
    # decode opcode; opcode is always last two digits, base 10
    inst = str(memory[pc])
    print(f"[debug] [{pc}]: {inst}")
    opcode = int(inst[-2:])
    pc += 1

    # Pad with 0s for missing parameter modes (leading 0s)
    param_count = ops[opcode].param_count
    inst = '0' * (2 + param_count - len(inst)) + inst
    print(f"[debug] (Padded to {inst})")

    # decode params
    params = []
    for i in range(param_count):
        params.append(Parameter(int(inst[-i - 3]), memory[pc]))
        print(f"[debug] [{pc}]: {memory[pc]}")
        pc += 1

    return (pc, Instruction(opcode, params))

# Runs an intcode program; memory is the starting memory contents. Returns the
# value at address 0 once the program halts (this is the program's output).
def intcode_run(memory):
    pc = 0
    while True:
        # Decode the next instruction.
        new_pc, inst = decode(memory, pc)

        print(f"[debug] [{pc:04x}] {inst}")

        opcode = inst.opcode
        if opcode == Opcode.ADD:
            s1, s2, d = inst.params
            assert(d.mode == ParameterMode.POSITION)
            memory[d.value] = s1.load(memory) + s2.load(memory)
        elif opcode == Opcode.MULTIPLY:
            s1, s2, d = inst.params
            assert(d.mode == ParameterMode.POSITION)
            memory[d.value] = s1.load(memory) * s2.load(memory)
        elif opcode == Opcode.INPUT:
            d, = inst.params
            assert(d.mode == ParameterMode.POSITION)
            # For now assume input must be integers
            v = int(input("> "))
            memory[d.value] = v
        elif opcode == Opcode.OUTPUT:
            s1, = inst.params
            print(f"[output] {s1.load(memory)}")
        elif opcode == Opcode.JT:
            s1, s2 = inst.params
            if s1.load(memory):
                new_pc = s2.load(memory)
        elif opcode == Opcode.JF:
            s1, s2 = inst.params
            if not s1.load(memory):
                new_pc = s2.load(memory)
        elif opcode == Opcode.LT:
            s1, s2, d = inst.params
            assert(d.mode == ParameterMode.POSITION)
            if s1.load(memory) < s2.load(memory):
                memory[d.value] = 1
            else:
                memory[d.value] = 0
        elif opcode == Opcode.EQ:
            s1, s2, d = inst.params
            assert(d.mode == ParameterMode.POSITION)
            if s1.load(memory) == s2.load(memory):
                memory[d.value] = 1
            else:
                memory[d.value] = 0
        elif opcode == Opcode.HALT:
            print("[debug] Program halted.")
            break
        else:
            raise ValueError(f"Invalid opcode: {opcode}")

        pc = new_pc
    # Result of program is in memory[0]
    return memory[0]

# Reads initial program memory from provided path, returns as a list.
def read_initial_memory(path):
    with open(path) as f:
        return [int(x) for x in f.readline().split(',')]
