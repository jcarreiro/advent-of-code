from collections import namedtuple
from enum import auto, IntEnum, Flag

# Size of Intcode machine "RAM". Chosen to be much larger than most programs.
MEMORY_SIZE = 4096

class Opcode(IntEnum):
    ADD = 1
    MULTIPLY = 2
    INPUT = 3
    OUTPUT = 4
    JT = 5
    JF = 6
    LT = 7
    EQ = 8
    INC_RB = 9
    HALT = 99

class ParameterMode(IntEnum):
    POSITION = 0   # Param is address
    IMMEDIATE = 1  # Param is immediate
    RELATIVE = 2   # Param is address relative to %rb.

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
    Opcode.INC_RB: Op(1),
    Opcode.HALT: Op(0),
}

class Parameter:
    def __init__(self, mode, value):
        self.mode = mode
        self.value = value

    def __str__(self):
        if self.mode == ParameterMode.IMMEDIATE:
            return f"${self.value}"
        elif self.mode == ParameterMode.RELATIVE:
            op = "+" if self.value > 0 else "-"
            return f"%rb {op} {abs(self.value)}"
        else:
            return str(self.value)

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
        self.pc = 0 # program counter
        self.rb = 0 # relative address base
        # Take a deep copy of memory so that changes in this machine can't
        # affect others which started from the same state.
        self.memory = memory.copy() + [0] * (MEMORY_SIZE - len(memory))
        assert(len(self.memory) == MEMORY_SIZE)
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.debug_flags = debug_flags

    def set_debug_flags(self, debug_flags):
        self.debug_flags = debug_flags

    def debug_log(self, channel, msg):
        if self.debug_flags & channel:
            print(f"[debug] [{channel}] {msg}")

    # Decode a single instruction; returns it and the new value of the pc.
    def decode(self, pc, memory):
        # decode opcode; opcode is always last two digits, base 10
        inst = str(memory[pc])
        self.debug_log(DebugFlags.DECODE, f"[{pc}]: {inst}")
        opcode = Opcode(int(inst[-2:]))
        pc += 1

        # Pad with 0s for missing parameter modes (leading 0s)
        param_count = ops[opcode].param_count
        inst = '0' * (2 + param_count - len(inst)) + inst

        # decode params
        params = []
        for i in range(param_count):
            params.append(Parameter(int(inst[-i - 3]), memory[pc]))
            self.debug_log(DebugFlags.DECODE, f"[{pc}]: {memory[pc]}")
            pc += 1

        return (pc, Instruction(opcode, params))

    # Compute an address. Not the same as loading a value!
    def effective_address(self, param):
        if param.mode == ParameterMode.POSITION:
            return param.value # address is absolute
        elif param.mode == ParameterMode.RELATIVE:
            return self.rb + param.value # address is relative to %rb
        else:
            raise ValueError(f"Invalid parameter mode for address: {param.mode}!")

    # Load a value from memory. For convenience, param may be IMMEDIATE, in
    # which case the immediate value is returned and no load is performed.
    def load(self, param):
        # Handle immediates for convenience.
        if param.mode == ParameterMode.IMMEDIATE:
            return param.value

        # This is a load from an address, compute the address.
        addr = None
        if param.mode == ParameterMode.RELATIVE:
            addr = self.rb + param.value
        elif param.mode == ParameterMode.POSITION:
            addr = param.value
        else:
            raise ValueError(f"Invalid address mode: {param.mode}!")

        value = self.memory[addr]
        self.debug_log(DebugFlags.MEMORY, f"Load from addr {addr}, value {value}.")
        return value

    # Stores value at the effective address of the given parameter.
    def store(self, param, value):
        addr = self.effective_address(param)
        self.memory[addr] = value
        self.debug_log(DebugFlags.MEMORY, f"Store to addr {addr}, value {value}.")

    def run(self):
        while True:
            # Decode the next instruction.
            new_pc, inst = self.decode(self.pc, self.memory)

            self.debug_log(DebugFlags.DECODE, f"[{self.pc:04x}] {inst}")

            opcode = inst.opcode
            if opcode == Opcode.ADD:
                s1, s2, d = inst.params
                self.store(d, self.load(s1) + self.load(s2))
            elif opcode == Opcode.MULTIPLY:
                s1, s2, d = inst.params
                self.store(d, self.load(s1) * self.load(s2))
            elif opcode == Opcode.INPUT:
                d, = inst.params
                # For now assume input must be integers
                v = int(self.input_fn("> "))
                self.debug_log(DebugFlags.INPUT, f"Got input {v}")
                self.store(d, v)
            elif opcode == Opcode.OUTPUT:
                s1, = inst.params
                self.output_fn(self.load(s1))
            elif opcode == Opcode.JT:
                s1, s2 = inst.params
                if self.load(s1):
                    new_pc = self.load(s2)
            elif opcode == Opcode.JF:
                s1, s2 = inst.params
                if not self.load(s1):
                    new_pc = self.load(s2)
            elif opcode == Opcode.LT:
                s1, s2, d = inst.params
                if self.load(s1) < self.load(s2):
                    self.store(d, 1)
                else:
                    self.store(d, 0)
            elif opcode == Opcode.EQ:
                s1, s2, d = inst.params
                if self.load(s1) == self.load(s2):
                    self.store(d, 1)
                else:
                    self.store(d, 0)
            elif opcode == Opcode.INC_RB:
                s1, = inst.params
                self.rb += self.load(s1)
                self.debug_log(DebugFlags.MEMORY, f"%rb = {self.rb}")
            elif opcode == Opcode.HALT:
                self.debug_log(DebugFlags.DECODE, "Program halted.")
                break
            else:
                raise ValueError(f"Invalid opcode: {opcode}")

            self.pc = new_pc

        # Result of program is in self.memory[0]
        return self.memory[0]

    def save_state(self):
        return {'pc': self.pc, 'rb': self.rb, 'memory': self.memory.copy()}

    def restore_state(self, state):
        self.pc = state['pc']
        self.rb = state['rb']
        self.memory = state['memory'].copy()


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
