#!/usr/bin/env python3

import logging
import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from solution import (
    BitStream,
    EqualToPacket,
    GreaterThanPacket,
    LessThanPacket,
    LiteralPacket,
    MaximumPacket,
    MinimumPacket,
    PacketType,
    ProductPacket,
    SumPacket,
    decode_packets,
    pretty_print,
    sum_packet_versions,
)

class TestBitStream(unittest.TestCase):
    def test_read(self):
        bs = BitStream("00")
        self.assertEqual(bs.read(1), 0)

        bs = BitStream("1f")
        bs.read(3)
        self.assertEqual(bs.read(5), 31)

        bs = BitStream("0ff0")
        bs.read(4)
        self.assertEqual(bs.read(8), 255)

class TestDecode(unittest.TestCase):
    def test_literal_packet(self):
        p = decode_packets("D2FE28")
        self.assertEqual(p.version, 6)
        self.assertEqual(p.type_id, 4)
        self.assertEqual(p.value, 2021)

    # TODO: implement __eq__ for operators, then simplify this code
    def test_operator_packet(self):
        p = decode_packets("38006F45291200")
        self.assertEqual(p.version, 1)
        self.assertEqual(p.type_id, 6)
        self.assertEqual(len(p.subpackets), 2)
        self.assertEqual(p.subpackets[0], LiteralPacket(6, 4, 10))
        self.assertEqual(p.subpackets[1], LiteralPacket(2, 4, 20))

        p = decode_packets("EE00D40C823060")
        self.assertEqual(p.version, 7)
        self.assertEqual(p.type_id, 3)
        self.assertEqual(len(p.subpackets), 3)
        self.assertEqual(p.subpackets[0], LiteralPacket(2, 4, 1))
        self.assertEqual(p.subpackets[1], LiteralPacket(4, 4, 2))
        self.assertEqual(p.subpackets[2], LiteralPacket(1, 4, 3))

def make_literal(value, version=0):
    return LiteralPacket(version, PacketType.LITERAL, value)

class TestOperators(unittest.TestCase):
    def check_multi_op(self, operator, version, type_id, test_cases):
        for subpackets, expected_value in test_cases:
            op = operator(version, type_id, subpackets)
            self.assertEqual(op.eval(), expected_value)

    def test_sum_new(self):
        self.check_multi_op(
            SumPacket,
            0,
            PacketType.SUM,
            [
                ([], 0),
                ([make_literal(1)], 1),
                ([make_literal(1), make_literal(2), make_literal(3)], 6),
            ],
        )

    def test_product(self):
        self.check_multi_op(
            ProductPacket,
            0,
            PacketType.PRODUCT,
            [
                ([], 0),
                ([make_literal(1)], 1),
                ([make_literal(2), make_literal(3), make_literal(4)], 24),
            ],
        )

    def test_min(self):
        self.check_multi_op(
            MinimumPacket,
            0,
            PacketType.MINIMUM,
            [
                ([make_literal(1)], 1),
                ([make_literal(2), make_literal(3), make_literal(4)], 2),
            ],
        )

    def test_max(self):
        self.check_multi_op(
            MaximumPacket,
            0,
            PacketType.MAXIMUM,
            [
                ([make_literal(1)], 1),
                ([make_literal(2), make_literal(3), make_literal(4)], 4),
            ],
        )

    def test_gt(self):
        self.check_multi_op(
            GreaterThanPacket,
            0,
            PacketType.GREATER_THAN,
            [
                ([make_literal(2), make_literal(3)], 0),
                ([make_literal(3), make_literal(2)], 1),
                ([make_literal(2), make_literal(2)], 0),
            ],
        )

    def test_lt(self):
        self.check_multi_op(
            LessThanPacket,
            0,
            PacketType.LESS_THAN,
            [
                ([make_literal(2), make_literal(3)], 1),
                ([make_literal(3), make_literal(2)], 0),
                ([make_literal(2), make_literal(2)], 0),
            ],
        )

    def test_eq(self):
        self.check_multi_op(
            EqualToPacket,
            0,
            PacketType.EQUAL_TO,
            [
                ([make_literal(2, version=0), make_literal(3, version=1)], 0),
                ([make_literal(3, version=0), make_literal(3, version=1)], 1),
            ],
        )

def decode_and_sum(message):
    return sum_packet_versions(decode_packets(message))

def decode_and_eval(message):
    return decode_packets(message).eval()

class TestSolution(unittest.TestCase):
    def test_version_sum(self):
        self.assertEqual(decode_and_sum("8A004A801A8002F478"), 16)
        self.assertEqual(decode_and_sum("620080001611562C8802118E34"), 12)
        self.assertEqual(decode_and_sum("C0015000016115A2E0802F182340"), 23)
        self.assertEqual(decode_and_sum("A0016C880162017C3686B18A3D4780"), 31)

    def test_eval(self):
        self.assertEqual(decode_and_eval("C200B40A82"), 3)
        self.assertEqual(decode_and_eval("04005AC33890"), 54)
        self.assertEqual(decode_and_eval("880086C3E88112"), 7)
        self.assertEqual(decode_and_eval("CE00C43D881120"), 9)
        self.assertEqual(decode_and_eval("D8005AC2A8F0"), 1)
        self.assertEqual(decode_and_eval("F600BC2D8F"), 0)
        self.assertEqual(decode_and_eval("9C005AC2F8F0"), 0)
        self.assertEqual(decode_and_eval("9C0141080250320F1802104A08"), 1)

if __name__ == '__main__':
    unittest.main()
