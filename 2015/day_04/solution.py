#!/usr/bin/env python3

import hashlib

def find_md5_hash_with_prefix(salt, prefix, max_steps=int(1e6)):
    print(f"Searching for MD5 hash with prefix {prefix}, using salt {salt}, max_steps = {max_steps}.")
    for i in range(max_steps):
        s = f"{salt}{i}"
        m = hashlib.md5()
        m.update(s.encode("ASCII"))
        digest = m.hexdigest()
        # print(f"{s} => {digest}")
        if digest.startswith(prefix):
            print(f"Found match: {s} => {digest}")
            return digest
    print(f"No match found in {max_steps} steps.")
    return None

def main():
    # For part 1, we need to find a hash with 5 leading zeros.
    print(find_md5_hash_with_prefix("bgvyzdsv", "00000"))

    # For part 2, we need 6 leading zeros.
    print(find_md5_hash_with_prefix("bgvyzdsv", "000000", int(1e7)))

if __name__ == "__main__":
    main()
