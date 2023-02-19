#!/usr/bin/env python3

import os
import sys
import unittest

from .solution import SnailNumber

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
                [[[[[9,8],1],2],3],4], [[[[0,9],2],3],4]
            ],
            [
                [7,[6,[5,[4,[3,2]]]]], [7,[6,[5,[7,0]]]]
            ],
            [
                [[6,[5,[4,[3,2]]]],1], [[6,[5,[7,0]]],3]
            ],
            [
                [[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]],
                [[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]],
            ],
            [
                [[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]],
                [[3,[2,[8,0]]],[9,[5,[7,0]]]],
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
            SnailNumber.add(a, b),
            SnailNumber.from_list([[[[0,7],4],[[7,8],[6,0]]],[8,1]]),
        )
