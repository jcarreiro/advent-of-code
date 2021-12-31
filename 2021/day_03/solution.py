#!/usr/bin/env python3

import numpy as np

def solve_part1(a):
    sums = np.sum(a.T, axis=1)
    print(sums)

    bits = (sums > a.shape[0] // 2).astype('uint8')
    print(bits)

    gamma = int(''.join(bits.astype('str')), base=2)
    epsilon = int(''.join(np.logical_not(bits).astype('uint8').astype('str')), base=2)
    print(f"gamma  = {gamma}, epsilon = {epsilon}, g * e = {gamma * epsilon}")

def solve_part2(A):
    def get_rating(A, comp):
        i = 0
        while A.shape[0] > 1 and i < A.shape[1]:
            # Get the most common bit in the next position.
            print(f"Checking column {i}, {A.T[i]}")
            b = comp(np.sum(A.T[i]), A.shape[0] / 2)
            print(f"Got bit: {b}")
            
            # Filter out the rows that don't match.
            A = A[A[:,i] == b]
            print(A)

            # Check the next column.
            i += 1
            
        # At this point we should only have one row left.
        assert(A.shape[0] == 1)
        return int(''.join(A[0].astype(str)), base=2)

    o2_rating = get_rating(A, lambda x, y: x >= y)
    co2_rating = get_rating(A, lambda x, y: x < y)
    print(f"O2 rating = {o2_rating}, CO2 rating = {co2_rating}, product = {o2_rating * co2_rating}")
        
def main():
    test_input = [
        "00100",
        "11110",
        "10110",
        "10111",
        "10101",
        "01111",
        "00111",
        "11100",
        "10000",
        "11001",
        "00010",
        "01010",
    ]

    with open("input.txt") as input_file:
        a = np.array([[int(x) for x in y.strip()] for y in input_file])
        print(a)
        print(f"Input array has dimensions: {a.shape}")
        solve_part2(a)

if __name__ == "__main__":
    main()
