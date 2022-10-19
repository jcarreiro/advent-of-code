#!/usr/bin/env python3

import logging
import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from solution import BitStream, LiteralPacket, decode_packets, sum_packet_versions

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

def decode_and_sum(message):
    return sum_packet_versions(decode_packets(message))
    
class TestVersionSum(unittest.TestCase):
    def test_version_sum(self):
        self.assertEqual(decode_and_sum("8A004A801A8002F478"), 16)
        self.assertEqual(decode_and_sum("620080001611562C8802118E34"), 12)
        self.assertEqual(decode_and_sum("C0015000016115A2E0802F182340"), 23)
        self.assertEqual(decode_and_sum("A0016C880162017C3686B18A3D4780"), 31)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
