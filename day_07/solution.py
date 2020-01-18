# Fix up sys.path so we can find intcode. Python imports suck.
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import intcode
import itertools

if __name__ == "__main__":
    # Read the initial program memory.
    memory = intcode.read_initial_memory("input")

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
