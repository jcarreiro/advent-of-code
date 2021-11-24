#!/usr/bin/env python3

import collections
import string

from enum import Enum, auto

test_circuit = """\
123 -> x
456 -> y
x AND y -> d
x OR y -> e
x LSHIFT 2 -> f
y RSHIFT 2 -> g
NOT x -> h
NOT y -> i
"""

test_output = """\
d: 72
e: 507
f: 492
g: 114
h: 65412
i: 65079
x: 123
y: 456
"""

###############################################################################
# Reading tokens
###############################################################################

class Operator(Enum):
    AND = auto()    # binary and
    OR = auto()     # binary or
    LSHIFT = auto() # left shift
    RSHIFT = auto() # right shift
    NOT = auto()    # binary negation
    ARROW = auto()  # assignment

class Token:
    class Type(Enum):
        NUMBER = auto() # numeric literal
        WIRE = auto()   # identifier
        OP = auto()     # operator

    def __init__(self, type, value):
        self.type = type
        self.value = value

# Reads the next token from the input.
def read_token(line, pos):
    # Read token from input.
    i = j = pos
    while j < len(line) and line[j] not in string.whitespace:
        j += 1

    token = line[i:j]
    print(f"Got token {token} at pos {i}, length {j-i}.")

    # Consume any whitespace after token.
    while j < len(line) and line[j] in string.whitespace:
        j += 1

    if token in ["AND", "OR", "LSHIFT", "RSHIFT", "NOT"]:
        return (Token(Token.Type.OP, Operator[token]), j)
    elif token == "->":
        return (Token(Token.Type.OP, Operator.ARROW), j)
    elif token.isdigit():
        return (Token(Token.Type.NUMBER, int(token)), j)
    elif token.isalpha():
        return (Token(Token.Type.WIRE, token), j)

def expect(line, token, expected):
    if token.type not in expected:
        raise ValueError(f"Invalid syntax: {line}")

def expect_op(line, token, expected):
    expect(line, token, [Token.Type.OP])
    if token.value != expected:
        raise ValueError(f"Invalid syntax: {line}")

def peek_token(line, pos):
    token, _ = read_token(line, pos)
    return token

###############################################################################
# Operator definitions.
###############################################################################

class LiteralOp:
    def __init__(self, value):
        self.value = value

    def apply(self, inputs):
        return self.value

    def to_string(self, input_wires):
        return f"{self.value}"

class AndOp:
    def apply(self, inputs):
        assert(len(inputs) == 2)
        return inputs[0] & inputs[1]

    def to_string(self, input_wires):
        return f"{input_wires[0]} AND {input_wires[1]}"

class OrOp:
    def apply(self, inputs):
        assert(len(inputs) == 2)
        return inputs[0] | inputs[1]

    def to_string(self, input_wires):
        return f"{input_wires[0]} OR {input_wires[1]}"

class NotOp:
    def apply(self, inputs):
        assert(len(inputs) == 1)
        return ~inputs[0]

    def to_string(self, input_wires):
        return f"NOT {input_wires[0]}"

class LShiftOp:
    def apply(self, inputs):
        assert(len(inputs) == 2)
        return inputs[0] << inputs[1]

    def to_string(self, input_wires):
        return f"{input_wires[0]} LSHIFT {input_wires[1]}"

class RShiftOp:
    def apply(self, inputs):
        assert(len(inputs) == 2)
        return inputs[0] >> inputs[1]

    def to_string(self, input_wires):
        return f"{input_wires[0]} RSHIFT {input_wires[1]}"

class IdentityOp:
    def apply(self, inputs):
        assert(len(inputs) == 1)
        return inputs[0]

    def to_string(self, input_wires):
        return str(input_wires[0])

class Expr:
    def __init__(self, inputs, op):
        self.inputs = inputs
        self.op = op

###############################################################################
# Parsing
###############################################################################

class Term:
    class Type(Enum):
        NUMBER = auto()
        WIRE = auto()

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return str(self.value)

# Parse a term, like "123", or "x".
def parse_term(line, pos):
    token, pos = read_token(line, pos)
    expect(line, token, [Token.Type.NUMBER, Token.Type.WIRE])
    if token.type == Token.Type.NUMBER:
        return (Term(Term.Type.NUMBER, int(token.value)), pos)
    elif token.type == Token.Type.WIRE:
        return (Term(Term.Type.WIRE, token.value), pos)
    else:
        raise ValueError("Unexpected token type: {token.type}")

# Parse an expression, like "x AND y", "NOT x", etc.
#
#   expr := term || term op term || "NOT" term
def parse_expr(line, pos):
    # Peek the next token
    token = peek_token(line, pos)

    # We expect either a term or a "NOT" to start the expr
    if token.type in [Token.Type.NUMBER, Token.Type.WIRE]:
        # This is a term; peek to see if there's a op, or if this
        # is just a bare term (e.g. "123 -> x" or "ab -> c").
        lhs, pos = parse_term(line, pos)
        token = peek_token(line, pos)
        if token.type == Token.Type.OP and token.value == Operator.ARROW:
            # This is an assignment like "123 -> x", just return.
            return (Expr([lhs], IdentityOp()), pos)
        else:
            # This must be an expression like "a OP b".
            token, pos = read_token(line, pos)
            expect(line, token, [Token.Type.OP])
            op = token.value

            # Read the RHS of the expression, then build the operator.
            rhs, pos = parse_term(line, pos)
            input_wires = [lhs, rhs]
            op_obj = None
            if op == Operator.AND:
                op_obj = AndOp()
            elif op == Operator.OR:
                op_obj = OrOp()
            elif op == Operator.LSHIFT:
                op_obj = LShiftOp()
            elif op == Operator.RSHIFT:
                op_obj = RShiftOp()
            else:
                raise ValueError(f"Unrecognized operator: {op}")
            return (Expr(input_wires, op_obj), pos)
    else:
        # Expression didn't start with a term, so it must be like "NOT x".
        token, pos = read_token(line, pos)
        expect(line, token, [Token.Type.OP])
        op = token.value
        if op != Operator.NOT:
            raise ValueError(f"Invalid syntax: {line}")

        rhs, pos = parse_term(line, pos)
        return (Expr([rhs], NotOp()), pos)

class Gate:
    def __init__(self, input_wires, op, output_wire):
        self.input_wires = input_wires
        self.op = op
        self.output_wire = output_wire

    def __str__(self):
        return f"Gate({self.op.to_string(self.input_wires)} -> {self.output_wire})"

    def _read_inputs(self, read_fn):
        inputs = []
        for term in self.input_wires:
            if term.type == Term.Type.NUMBER:
                inputs.append(term.value)
            elif term.type == Term.Type.WIRE:
                inputs.append(read_fn(term.value))
            else:
                raise ValueError(f"Unrecognized term type: {term.type}")
        return inputs
    
    def apply(self, read_fn, write_fn):
        print(f"Applying {self}.")

        # Get input values by reading wire values; note inputs can also be
        # numbers!
        inputs = self._read_inputs(read_fn)
        print(f"Got inputs: {inputs}.")

        # Check if we're ready to apply this gate.
        if None in inputs:
            print(f"Input missing for gate {self}, skipped.")
        else:
            # Note that wire values are always 16-bit. So truncate on each
            # write back to "memory" here.
            output = self.op.apply(inputs) & 0xffff
            write_fn(self.output_wire, output)

def parse_wire(line, pos):
    token, pos = read_token(line, pos)
    expect(line, token, [Token.Type.WIRE])
    return (token.value, pos)

def parse_gate(line):
    # Read the expression for this gate.
    pos = 0
    expr, pos = parse_expr(line, pos)

    # Check for the expected arror operator.
    token, pos = read_token(line, pos)
    expect_op(line, token, Operator.ARROW)

    # Read the output wire name for this gate.
    wire, pos = parse_wire(line, pos)

    # build and return the gate object
    return Gate(expr.inputs, expr.op, wire)

class Simulation:
    def __init__(self):
        self.gates = []
        self.overrides = {}

    def load_gates(self, gate_defs):
        for line in gate_defs:
            line = line.strip()
            print(line)

            # The grammar looks like this:
            #
            #   gate  => expr "->" wire
            #   expr  => term || term op term || "NOT" term
            #   term  => number || wire_name
            #   op    => "AND" || "OR" || "LSHIFT" || "RSHIFT"
            #
            # We call everything a gate, even if it's a fixed value ("123 -> a").
            gate = parse_gate(line)
            print(gate)
            self.gates.append(gate)
        
    def pin(self, wire, value):
        """Pins a wire to a specific value."""
        self.overrides[wire] = value

    def run(self):
        wires = collections.defaultdict(lambda: None)
        wire_value_changed = True
        
        def read_wire(w):
            if w in self.overrides:
                return self.overrides[w]
            return wires[w]

        def write_wire(w, v):
            nonlocal wire_value_changed            
            print(f"{w} <- {v}")
            if wires[w] != v and w not in self.overrides:
                wire_value_changed = True
                wires[w] = v

        # "Run" the circuit by applying each gate at each time step until the
        # wire values stop changing.
        t = 1
        while wire_value_changed:
            wire_value_changed = False
            print(f"Running time step: {t}")
            for g in self.gates:
                g.apply(read_wire, write_wire)
            t += 1

        print(f"Final wire values at time step {t}:")
        for w in sorted(wires.keys()):
            print(f"{w}: {wires[w]}")

def main():
    simulation = Simulation()
    with open("input.txt") as input_file:
        simulation.load_gates(input_file)
    simulation.run()

    print("Re-running simulation for part 2...")
    simulation.pin('b', 46065)
    simulation.run()

if __name__ == "__main__":
    main()
