from collections import namedtuple
from enum import auto, IntEnum, Flag

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

class DebugFlags(Flag):
    DECODE = auto() # instruction decode
    MEMORY = auto() # all memory reads and writes
    INPUT  = auto() # input operations
    ALL    = DECODE | MEMORY | INPUT

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

    def __str__(self):
        prefix = ""
        if self.mode == ParameterMode.IMMEDIATE:
            prefix += "$"
        return prefix + str(self.value)

    def load(self, memory):
        if self.mode == ParameterMode.IMMEDIATE:
            return self.value
        return memory[self.value]

class Instruction:
    def __init__(self, opcode, params):
        self.opcode = opcode
        self.params = params

    def __str__(self):
        s = str(self.opcode) + " " + ", ".join([str(p) for p in self.params])
        s += " ("
        s += "".join([str(p.mode) for p in self.params]) + f"{self.opcode:02}"
        if self.params:
            s += "," + ",".join([str(p.value) for p in self.params])
        s += ")"
        return s


class IntcodeMachine:
    # Create an Intcode machine with the given initial memory contents.
    # input_fn can be used to provide an alternate input method (e.g. a
    # generator); the function must take one parameter (the prompt to
    # display) and return a string.
    def __init__(
            self,
            memory,
            input_fn=input,
            output_fn=lambda v: print(f"[output] {v}"),
            debug_flags=DebugFlags(0)):
        # Take a deep copy of memory so that changes in this machine can't
        # affect others which started from the same state.
        self.pc = 0
        self.memory = memory[:]
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.debug_flags = debug_flags

    def set_debug_flags(self, debug_flags):
        self.debug_flags = debug_flags

    def debug_log(self, channel, msg):
        if self.debug_flags & channel:
            print(f"[debug] [{channel}] {msg}")

    # Decode a single instruction; returns it and the new value of the pc.
    def decode(self):
        # decode opcode; opcode is always last two digits, base 10
        pc = self.pc
        inst = str(self.memory[pc])
        self.debug_log(DebugFlags.DECODE, f"[{pc}]: {inst}")
        opcode = Opcode(int(inst[-2:]))
        pc += 1

        # Pad with 0s for missing parameter modes (leading 0s)
        param_count = ops[opcode].param_count
        inst = '0' * (2 + param_count - len(inst)) + inst
        self.debug_log(DebugFlags.DECODE, f"(Padded to {inst})")

        # decode params
        params = []
        for i in range(param_count):
            params.append(Parameter(int(inst[-i - 3]), self.memory[pc]))
            self.debug_log(DebugFlags.DECODE, f"[{pc}]: {self.memory[pc]}")
            pc += 1

        return (pc, Instruction(opcode, params))

    def run(self):
        pc = 0
        while True:
            # Decode the next instruction.
            new_pc, inst = self.decode()

            self.debug_log(DebugFlags.DECODE, f"[{pc:04x}] {inst}")

            opcode = inst.opcode
            if opcode == Opcode.ADD:
                s1, s2, d = inst.params
                assert(d.mode == ParameterMode.POSITION)
                self.memory[d.value] = s1.load(self.memory) + s2.load(self.memory)
            elif opcode == Opcode.MULTIPLY:
                s1, s2, d = inst.params
                assert(d.mode == ParameterMode.POSITION)
                self.memory[d.value] = s1.load(self.memory) * s2.load(self.memory)
            elif opcode == Opcode.INPUT:
                d, = inst.params
                assert(d.mode == ParameterMode.POSITION)
                # For now assume input must be integers
                v = int(self.input_fn("> "))
                self.debug_log(DebugFlags.INPUT, f"Got input {v}")
                self.memory[d.value] = v
            elif opcode == Opcode.OUTPUT:
                s1, = inst.params
                self.output_fn(s1.load(self.memory))
            elif opcode == Opcode.JT:
                s1, s2 = inst.params
                if s1.load(self.memory):
                    new_pc = s2.load(self.memory)
            elif opcode == Opcode.JF:
                s1, s2 = inst.params
                if not s1.load(self.memory):
                    new_pc = s2.load(self.memory)
            elif opcode == Opcode.LT:
                s1, s2, d = inst.params
                assert(d.mode == ParameterMode.POSITION)
                if s1.load(self.memory) < s2.load(self.memory):
                    self.memory[d.value] = 1
                else:
                    self.memory[d.value] = 0
            elif opcode == Opcode.EQ:
                s1, s2, d = inst.params
                assert(d.mode == ParameterMode.POSITION)
                if s1.load(self.memory) == s2.load(self.memory):
                    self.memory[d.value] = 1
                else:
                    self.memory[d.value] = 0
            elif opcode == Opcode.HALT:
                self.debug_log(DebugFlags.DECODE, "Program halted.")
                break
            else:
                raise ValueError(f"Invalid opcode: {opcode}")

            self.pc = new_pc

        # Result of program is in self.memory[0]
        return self.memory[0]

# Runs an intcode program; memory is the starting memory contents. Returns the
# value at address 0 once the program halts (this is the program's output).
def intcode_run(memory):
    # For back compat with old solutions.
    return IntcodeMachine(memory).run()

# Reads initial program memory from provided path, returns memory contents as
# a list, where index 0 in the list is cell 0 of memory.
def read_initial_memory(path):
    with open(path) as f:
        memory = []
        # todo: ignore lines starting with ';' (comments)
        for line in f:
            memory.extend([int(x) for x in line.rstrip().split(',')])
        return memory
