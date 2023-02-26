#!/usr/bin/env python3

import os
import sys
import unittest

from .solution import SnailNumber, sum_list, solve_part1

class TestSnailNumber(unittest.TestCase):
    def test_from_list(self):
        sn = SnailNumber.from_list([1,2])
        self.assertEqual(sn.to_list(), [1,2])

        sn = SnailNumber.from_list([[1,2],3])
        self.assertEqual(sn.to_list(), [[1,2],3])

        sn = SnailNumber.from_list([1,[2,3]])
        self.assertEqual(sn.to_list(), [1,[2,3]])

    def test_explode(self):
        TEST_CASES = [
            [
                # Case 1: [9,8] explodes, the 8 is added to the 1, the 9 is lost.
                [[[[[9,8],1],2],3],4], [[[[0,9],2],3],4]
            ],
            [
                # Case 2: [3,2] explodes, the 3 is added to the 4, the 2 is lost.
                [7,[6,[5,[4,[3,2]]]]], [7,[6,[5,[7,0]]]]
            ],
            [
                # Case 3: [3,2] explodes, the 3 is added to the 4, the 2 to the 1.
                [[6,[5,[4,[3,2]]]],1], [[6,[5,[7,0]]],3]
            ],
            [
                # Case 4: [7,3] explodes, the 7 is added to the 1, the 3 to the 6.
                [[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]],
                [[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]],
            ],
            [
                # Case 5: [3,2] explodes, the 3 is added to the 4, the 2 is lost.
                [[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]],
                [[3,[2,[8,0]]],[9,[5,[7,0]]]],
            ],
            [
                # Case 6: Like 3), but the right side is not a simple number, so
                # we need to find the successor value and add the 2 to that.
                [[6,[5,[4,[3,2]]]],[[1,2],3]], [[6,[5,[7,0]]],[[3,2],3]]
            ],
            [
                # Case 7: Like 6), but mirrored so that we need to find the
                # predecessor instead of the successor.
                [[3,[2,1]],[[[[2,3],4],5],6]], [[3,[2,3]], [[[0,7],5],6]]
            ],
        ]
        for tc in TEST_CASES:
            sn = SnailNumber.from_list(tc[0]).explode()
            self.assertEqual(sn.to_list(), tc[1])

    def test_split(self):
        TEST_CASES = [
            [
                [10, 0], [[5, 5], 0],
                [11, 0], [[5, 6], 0],
            ],
        ]
        for tc in TEST_CASES:
            sn = SnailNumber.from_list(tc[0]).split()
            self.assertEqual(sn.to_list(), tc[1])

    def test_add(self):
        # [[[[4,3],4],4],[7,[[8,4],9]]] + [1,1] = [[[[0,7],4],[[7,8],[6,0]]],[8,1]]
        a = SnailNumber.from_list([[[[4,3],4],4],[7,[[8,4],9]]])
        b = SnailNumber.from_list([1,1])
        self.assertEqual(
            a + b,
            SnailNumber.from_list([[[[0,7],4],[[7,8],[6,0]]],[8,1]]),
        )

    def test_magnitude(self):
        TEST_CASES = [
            [[9,1], 29],
            [[[1,2],[[3,4],5]], 143],
            [[[[[0,7],4],[[7,8],[6,0]]],[8,1]], 1384],
            [[[[[1,1],[2,2]],[3,3]],[4,4]], 445],
            [[[[[3,0],[5,3]],[4,4]],[5,5]], 791],
            [[[[[5,0],[7,4]],[5,5]],[6,6]], 1137],
            [[[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]], 3488],
        ]
        for tc in TEST_CASES:
            self.assertEqual(SnailNumber.from_list(tc[0]).magnitude(), tc[1])

    def test_list_sum(self):
        TEST_CASES = [
            (
                [
                    [1,1],
                    [2,2],
                    [3,3],
                    [4,4],
                ],
                [[[[1,1],[2,2]],[3,3]],[4,4]],
            ),
            (
                [
                    [1,1],
                    [2,2],
                    [3,3],
                    [4,4],
                    [5,5],
                ],
                [[[[3,0],[5,3]],[4,4]],[5,5]],
            ),
            (
                [
                    [1,1],
                    [2,2],
                    [3,3],
                    [4,4],
                    [5,5],
                    [6,6],
                ],
                [[[[5,0],[7,4]],[5,5]],[6,6]],
            ),
            (
                [
                    [[[0,[4,5]],[0,0]],[[[4,5],[2,6]],[9,5]]],
                    [7,[[[3,7],[4,3]],[[6,3],[8,8]]]],
                    [[2,[[0,8],[3,4]]],[[[6,7],1],[7,[1,6]]]],
                    [[[[2,4],7],[6,[0,5]]],[[[6,8],[2,8]],[[2,1],[4,5]]]],
                    [7,[5,[[3,8],[1,4]]]],
                    [[2,[2,2]],[8,[8,1]]],
                    [2,9],
                    [1,[[[9,3],9],[[9,0],[0,7]]]],
                    [[[5,[7,4]],7],1],
                    [[[[4,2],2],6],[8,7]],
                ],
                [[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]],
            ),
        ]
        for tc in TEST_CASES:
            self.assertEqual(
                sum_list([str(n) for n in tc[0]]),
                SnailNumber.from_list(tc[1]),
            )

    def test_homework(self):
        sum_ = sum_list(
            [
                str(n) for n in [
                    [[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]],
                    [[[5,[2,8]],4],[5,[[9,9],0]]],
                    [6,[[[6,2],[5,6]],[[7,6],[4,7]]]],
                    [[[6,[0,7]],[0,9]],[4,[9,[9,0]]]],
                    [[[7,[6,4]],[3,[1,3]]],[[[5,5],1],9]],
                    [[6,[[7,3],[3,2]]],[[[3,8],[5,7]],4]],
                    [[[[5,4],[7,7]],8],[[8,3],8]],
                    [[9,3],[[9,9],[6,[4,9]]]],
                    [[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]],
                    [[[[5,2],5],[8,[3,7]]],[[5,[7,5]],[4,4]]],
                ]
            ],
        )
        self.assertEqual(
            sum_,
            SnailNumber.from_list(
                [[[[6,6],[7,6]],[[7,7],[7,0]]],[[[7,7],[7,7]],[[7,8],[9,9]]]],
            ),
        )
        self.assertEqual(sum_.magnitude(), 4140)
