#!/usr/bin/env python3

import numpy as np

# Read an np.array from a file of digits (i.e., 0-9).
def read_array_from_file(f):
    l = []
    for line in f:
        l.append([int(x) for x in line.strip()])
    return np.array(l)
