#!/usr/bin/env python3

import datetime
import math
import multiprocessing
import numpy as np
import time

from scipy import int8
from scipy.sparse import lil_matrix

# Builds an NxN sparse matrix, using the rules from the problem:
#
# 1. The base_pattern repeats.
# 2. Each row in the matrix has each element in the pattern repeated i times,
#    where i is the row index + 1 (e.g. twice in the second row).
# 3. The whole pattern is shifted one place "to the left".
def build_sparse_pattern_matrix(base_pattern, input_len):
    m = lil_matrix((input_len, input_len), dtype=int8)
    for i in range(input_len):
#        print(f"i = {i}")
        j = 0 # position in output matrix
        k = 0 # position in pattern; repeats.
        while j < input_len:
#            print(f"j = {j}, k = {k}")
            # Add i copies of the next digit from the pattern.
            copy_count = i + 1
            if j == 0 and k == 0:
                # Skip the first digit in the row.
                copy_count -= 1
            if copy_count:
                copy_count = min(copy_count, input_len - j)
                if base_pattern[k] != 0:
                    m[i,j:j+copy_count] = base_pattern[k]
            j += copy_count
            k = (k + 1) % len(base_pattern)
    return m.tocsc() # or maybe csr?

def get_pattern_row(base_pattern, input_len, output_pos):
    pattern = []
    for x in base_pattern:
        pattern += [x] * (output_pos + 1)

    # Note the plus 1 here is because we shift the whole pattern left once.
    j = input_len + 1

    # Copy pattern enough times to cover the whole input.
    n = math.ceil(j / len(pattern))
    if n > 1:
        pattern = pattern * n

    # Note the [1:] here is to skip the first digit of the pattern.
    return pattern[1:j]

def build_dense_pattern_matrix(base_pattern, input_len):
    rows = []
    # We're going to have as many rows as their are numbers in our input list.
    for i in range(input_len):
        rows.append(get_pattern_row(base_pattern, input_len, i))
    return np.array(rows)

def solve_part1(input_list, phases):
    base_pattern = [0, 1, 0, -1]

    # v is the input vector.
    v = np.array([input_list]).T
    print(f"v has dimensions {v.shape}.")

    # N is the "pattern matrix".
    N = build_dense_pattern_matrix(base_pattern, len(input_list))
    print(f"N has dimensions {N.shape}.")

    # Now we apply the pattern matrix for P phases to get our output.
    for phase in range(phases):
        print(f"Processing phase {phase}.")
        v = N.dot(v)
        v = np.mod(np.abs(v), 10)
#        print(v)
    return v.flatten().tolist()

# TODO: this doesn't work. The pattern matrix for even just the examples
# below is too big to fit in memory (~100 GB, or if we used a sparse
# matrix maybe ~50 GB since it's all 0s below the diagonal).
def solve_part2(input_list, phases):
    # In part 2, we have to repeat the input list 10,000 times to get the "real"
    # input!
    output = solve_part1(input_list * 10000, 100)

    # Then, to find the answer, we take the first seven digits of our input as
    # our "message offset", and find the eight digits at that offset in the
    # output.
    offset = int(''.join([str(x) for x in input[0:7]]))
    return output[offset:offset + 8]

def solve_part2_alt(input_list, phases):
    base_pattern = [0, 1, 0, -1]

    # In this version we only store the current output vector to reduce the
    # memory usage.
    n = len(input_list)
    v = np.array([input_list])
    for phase in range(phases):
        print(f"Processing phase {phase}.")
        w = np.zeros((1, n))
        for j in range(n):
            pct_done = float(j) / float(n)
            print(f"Phase {phase}, position {j} / {n} ({pct_done:0.2%}).")
            p = np.array([get_pattern_row(base_pattern, n, j)])
#            print(p)
            w[0][j] = np.mod(np.abs(np.dot(v, p.T)), 10)
        v = w
        print(v)
    return v.flatten().tolist()

# Computes every n-th digit of the output (e.g offset 1, skip count of 2 means
# compute every other digit, starting at index 1 in the output).
def compute_output(input_array, output_array, offset=0, skip_count=1):
    n = len(input_array)
    v = input_array
    w = output_array
    i = 0      # position in input vector
    j = offset # position in output vector
    # start = time.monotonic()
    while j < n:
        acc = 0
        neg = False
        rep_count = j + 1

        # print(f"j = {j}, rep_count = {rep_count}.")

        # pct_done = float(j) / float(n)
        # delta = time.monotonic() - start
        # dps = j / delta
        # eta = "inf"
        # if dps:
        #     eta = datetime.timedelta(seconds=(n - j) / dps)
        # print(f"[Phase {phase}] {j} digits out of {n} done ({pct_done:0.02%}, {dps:0.3} dps, eta {eta}).")

        # Skip the first j + 1 - 1 positions. These are always 0s in the
        # pattern, since we have j + 1 repeated 0s at the start, minus one for
        # the "left shift" of the whole pattern.
        i = rep_count - 1
        while i < n:
            # print(f"acc = {acc}, neg = {neg}, i = {i}.")

            # Sum the next j + 1 input digits (we know there are j + 1
            # repeats of each pattern digit).
            x = sum(v[i:i+rep_count])

            # If the position in the pattern was a '-1', flip the sign of
            # the sum (since it really was -a - b - c...).
            if neg:
                x = -x
            neg = not neg

            # Add the value to the accumulator.
            acc += x

            # Skip ahead to next non-zero position in pattern. There are
            # always j zeros to skip, plus we used j terms of the input,
            # for a total of 2j.
            i += 2 * rep_count

        # The output is always the ones digit, so take the abs value of the
        # accumulator, mod 10.
        w[j] = abs(acc) % 10

        # print(f"w[{j}] = abs({acc}) % 10 ({w[-1]})")

        j += skip_count

# Well, numpy didn't work. This takes direct advantage of the specific pattern
# to try to skip as much work as possible when computing "phases".
#
# Tried it, still seems like it's going to take way to long... :(
#
# Let's try to just throw more cores at it?
def solve_part2_alt2(input_list, phases, out_offset=0, out_len=8):
    n = len(input_list)
    start = time.monotonic()
    for phase in range(1, phases+1):
        pct_done = float(phase - 1) / float(phases)
        delta = time.monotonic() - start
        pps = float(phase - 1) / float(delta)
        eta = "inf"
        if pps > 0:
            eta = datetime.timedelta(seconds=(phases - phase) / pps)
        print(f"Processing phase {phase} / {phases} ({pct_done:0.02%}, {pps:0.3} pps, eta {eta}).")

        v = multiprocessing.Array('i', input_list, lock=False)
        w = multiprocessing.Array('i', n, lock=False)

        # TODO: probably be faster to use a queue so we don't need to fork
        # off all the child processes for each phase.
        num_procs = 10 # set to 2 x num cores for best performance
        args = []
        for i in range(num_procs):
            args.append((v, w, i, num_procs))
        processes = list(map(
            lambda args: multiprocessing.Process(target=compute_output, args=args),
            args))
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        input_list=list(w)
    return input_list[out_offset:out_len]

if __name__ == "__main__":
    # This is the first example in the problem. After 4 phases, the output
    # should be 0, 1, 0, 2, 9, 4, 9, 8.
    example_1 = list(range(1, 9))

    # This is the second example. After 100 phases, the first eight digits
    # of the output should be 2, 4, 1, 7, 6, 1, 7, 6.
    example_2 = [8, 0, 8, 7, 1, 2, 2, 4, 5, 8, 5, 9, 1, 4, 5, 4, 6, 6, 1, 9, 0,
                 8, 3, 2, 1, 8, 6, 4, 5, 5, 9, 5]

    def make_number_list(s):
        return [int(d) for d in s]

    # "19617804207202209144916044189917 becomes 73745418" after 100 phases.
    example_3 = make_number_list("19617804207202209144916044189917")

    # "69317163492948606335995924319873 becomes 52432133" after 100 phases.
    example_4 = make_number_list("69317163492948606335995924319873")

    def read_number_list(filename):
        with open(filename, "r") as f:
            return make_number_list(f.readline().strip())

    # These are the examples for part 2 (note the input should be repeated
    # 10,000 times):
    #
    # 03036732577212944063491565474664 becomes 84462026.
    # 02935109699940807407585447034323 becomes 78725270.
    # 03081770884921959731165446850517 becomes 53553731.
    example_5 = make_number_list("03036732577212944063491565474664")
    example_6 = make_number_list("02935109699940807407585447034323")
    example_7 = make_number_list("03081770884921959731165446850517")

    def list_to_int(l):
        return int(''.join([str(x) for x in l]))

    # This was from part 1.
    # output = solve_part2_alt2(read_number_list("input"), 100)
    # print(''.join([str(x) for x in output]))

#    output = solve_part2_alt2(example_5 * 10000, 100, 303673, 8)
    output = solve_part2_alt2(example_1, 4)
    print(''.join([str(x) for x in output]))
