#!/usr/bin/env python3

if __name__ == "__main__":
    with open("input.txt") as input:
        s = input.readline()
        print(f"Got input: {s}")
        open_count = s.count("(")
        close_count = s.count(")")
        print(
            f"Got open count: {open_count}, close count: {close_count}, solution: "
            f"{open_count - close_count}."
        )

        floor = 0
        for i in range(len(s)):
            x = s[i]
            if x == "(":
                floor += 1
            elif x == ")":
                floor -= 1
                if floor == -1:
                    print(f"First entered basement on character {i+1}.")
                    break
