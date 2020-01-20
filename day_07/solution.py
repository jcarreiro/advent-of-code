# Fix up sys.path so we can find intcode. Python imports suck.
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import intcode
import itertools

# In part 1, the 5 amplifiers are wired in series:
#
#   input -> [Amp 1] -> [Amp 2] -> [Amp 3] -> [Amp 4] -> [Amp 5] -> output
#
# Each amp gets two parameters as input, the phase setting (digit from 0 - 4,
# inclusive) and the input (output from last stage, 0 for amp 1).
#
# The solution to the problem is the maximum output obtained by varying the
# phase settings (note that each digit can only be used once).
def solve_part1(memory):
    # Run the 5 machines; each machine's input is the chosen phase setting,
    # followed by the output of the last machine (0 for the first machine).
    # Note that all machines have the same program (same initial memory
    # contents).
    max_output = None
    for phases in itertools.permutations("01234", 5):
        print(f"Trying phase sequence {phases}.")
        i = 0
        output = 0 # first machine gets a 0 for thrust level
        for p in phases:
            # Set up the input fn for this machine.
            inputs = [p, output]
            outputs = []

            print(f"Running machine {i} with phase {p} and input {output}.")

            m = intcode.IntcodeMachine(
                memory,
                lambda _: inputs.pop(0),
                lambda x: outputs.append(x),
                debug_flags=intcode.DebugFlags(0))
            m.run()
            # Program only have produced a single output!
            assert(len(outputs) == 1)
            output = outputs.pop()
            print(f"Got output {output}.")
            i += 1

        # Check to see if the resulting thrust level is the max.
        if not max_output:
            max_output = output
        else:
            max_output = max(output, max_output)

    print(f"Max output was {max_output}.")

# Part 2 is similar to part 1, but now the amps are set up as a feedback loop:
# the output of amp 5 is fed back into amp 1 repeatedly, until all the machines
# halt. The phase settings also now must be in the range 5 to 9.
def solve_part2(memory):
    class InputException(BaseException):
        pass

    class Amplifier:
        def __init__(self, label, memory):
            self.label = label
            self.machine = intcode.IntcodeMachine(
                memory,
                self.handle_input,
                self.handle_output,
                debug_flags=intcode.DebugFlags.ALL,
            )
            self.inputs = []
            self.output = None

        def run(self):
            self.machine.run()

        def push_input(self, v):
            self.inputs.append(v)

        def handle_input(self, _):
            try:
                return self.inputs.pop(0)
            except IndexError:
                raise InputException()

        def get_input(self):
            return self.inputs

        def handle_output(self, v):
            self.output.append(v)

        def set_output(self, output):
            self.output = output

    max_output = None
    for phases in itertools.permutations("56789", 5):
        labels = list('ABCDE')
        amps = []
        for phase in phases:
            label = labels.pop(0)
            print(f"Creating amplifier {label} with phase setting {phase}.")
            amp = Amplifier(label, memory)
            amp.push_input(phase)
            amps.append(amp)

        # rebind outputs to next machine in list
        for i in range(4):
            amps[i].set_output(amps[i + 1].get_input())

        # last amp's output is a special case
        amps[-1].set_output(amps[0].get_input())

        # the first machine gets a 0 as the second input on the first run
        # (after that it gets the last output from 'E').
        amps[0].push_input('0')

        # run until the last amp ('E') has halted; the last output from E
        # is the signal sent to the thrusters.
        i = 0
        while True:
            amp = amps[i]
            print(f"Running amplifier {amp.label}.")
            try:
                # run machine until we underflow the input
                amp.run()

                # if we get here the machine halted -- if this is the last
                # amp ('E') then we're done
                if amp.label == 'E':
                    break
            except InputException:
                # loop and run next machine in list
                print(f"Amplifier {amp.label} raised input exception, running next amp.")

            i = (i + 1) % len(amps)

        # Done running all amps, check output against current max.
        output = amps[0].get_input().pop(0)
        print(f"Amp E's final output was {output}.")
        if not max_output or output > max_output:
            max_output = output

    print(f"Max output was {max_output}.")

if __name__ == "__main__":
    # Read the initial program memory.
    memory = intcode.read_initial_memory("input")
    solve_part2(memory)
