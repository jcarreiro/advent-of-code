#!/usr/bin/env python3

def main():
    # In part 1, we need to count the number of times the depth increases in our
    # sonar readings.
    #
    # depths = [199, 200, 208, 210, 200, 207, 240, 269, 260, 263]
    with open("input.txt") as input_file:
        depths = [int(l.strip()) for l in input_file]
        c = 0
        for i in range(len(depths)):
            if i > 0 and depths[i] > depths[i-1]:
                c += 1
        print(f"Found {c} depth increases in part 1.")

    # In part 2, we need to count the number of times the sum of last 3 elements
    # decreases (e.g., we need to compare a[i-4:i] to a[i-3:i+1] for all i, but
    # we can avoid needing to recompute the partial sums all the time).
    with open("input.txt") as input_file:
        depths = [int(l.strip()) for l in input_file]
        # depths = [199, 200, 208, 210, 200, 207, 240, 269, 260, 263]
        window = 0
        c = 0
        for i in range(len(depths)):
            # Save the current sum.
            last_window = window
            
            # Add i into the sliding window and remove i-3 to get our new sum.
            window += depths[i]

            if i > 2:
                window -= depths[i-3]

                # Compare the sums and iterate.
                print(f"i = {i}, sum = {window}, last sum = {last_window}")
                if window > last_window:
                    c += 1
        print(f"Found {c} depth increases in part 2.")

if __name__ == "__main__":
    main()
