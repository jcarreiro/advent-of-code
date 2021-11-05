def solve_part1_exhaustive(lower_bound, upper_bound):
    # Check each number for:
    #   1. two adjacent digits must be the same
    #   2. the digits never decrease from left to right
    count = 0
    for x in range(lower_bound, upper_bound):
        print(f"Checking {x}")
        s = str(x)
        digits_decrease = False
        found_double = False
        for i in range(len(s) - 1):
            if not found_double and s[i] == s[i+1]:
                found_double = True
            if int(s[i+1]) < int(s[i]):
                digits_decrease = True
                break

        if digits_decrease:
            print("Digits decrease, skipped.")
            continue

        if not found_double:
            print("No double, skipped.")
            continue

        print(f"Accepted {x} as possible passcode.")
        count += 1

    print(f"There are {count} possible passwords in the range {lower_bound} - {upper_bound}.")

def solve_part2_exhaustive(lower_bound, upper_bound):
    # Check each number for:
    #   1. two adjacent digits must be the same
    #   2. the digits never decrease from left to right
    #   3. the two adjacent matching digits must not be part of a larger group
    #      of matching digits
    count = 0
    for x in range(lower_bound, upper_bound):
        print(f"Checking {x}: ", end='')
        s = str(x)
        digits_decrease = False
        found_double = False
        for i in range(len(s) - 1):
            if not found_double and s[i] == s[i+1]:
                found_double = True
                print(f"i={i}, s[i]={s[i]}, s[i+1]={s[i+1]}")
                # double check that we're not part of a larger group
                if i < len(s) - 2 and s[i] == s[i+2]:
                    print(f"s[i+2]={s[i+2]}")
                    found_double = False
                if i > 0 and s[i] == s[i-1]:
                    print(f"s[i-1]={s[i-1]}")
                    found_double = False

            if int(s[i+1]) < int(s[i]):
                digits_decrease = True
                break

        if digits_decrease:
            print("Digits decrease, skipped.")
            continue

        if not found_double:
            print("No double, skipped.")
            continue

        print("Accepted")
        count += 1

    print(f"There are {count} possible passwords in the range {lower_bound} - {upper_bound}.")


def solve_part1():
    # Note that there is only one possible password for a 2 digit number, since
    # the digits must be the same (e.g. '00'). For more than two digits, we can
    # first find the total number of possible passwords, then subtract those
    # that don't meet the "repeated digit" requirement.
    #
    # First note that for two digits, ignoring the issue of repeat digits, there
    # are:
    #
    #   1 possible passwords for a leading 9 (99)
    #   2 possible passwords for a leading 8 (88, 89)
    #   3 possible passwords for a leading 7 (77, 78, 79)
    #   ...
    #   10 possible passwords for a leading 0 (00, 01, 02, ... 09)
    #
    # Now consider the case for 3 digit paswords. Then the number of possible
    # passwords, again ignoring the issue of repeat digits, is:
    #
    #   1 possible passwords for a leading 9 (999)
    #   3 possible passwords for a leading 8 (888, 889, 899)
    #   6 possible passwords for a leading 7 (777, 778, 779, 788, 789, 799)
    #   ...
    #   \sum{k}{9} 10 - k passwords for a leading k
    #
    # So what about 4 digits?
    #
    #   1  possible passwords for a leading 9 (9999)
    #   4  possible passwords for a leading 8 (8888, 8889, 8899, 8999)
    #   10 possible passwords for a leading 7 (7777, 7778, 7779, 7788, 7789,
    #                                          7799, 7888, 7889, 7899, 7999)
    #   ...
    #   \sum{k}{9} \sum{k}{9} 10 - k
    #
    # This pattern holds for any number of digits.
    #
    # But how do we deal with the range given in the problem?
    pass

if __name__ == '__main__':
    lower_bound = 356261
    upper_bound = 846303
    # solve_part1_exhaustive(lower_bound, upper_bound)
    solve_part2_exhaustive(lower_bound, upper_bound)
