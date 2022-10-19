#!/usr/bin/env python3

import argparse
import logging

from enum import IntEnum

class BitStream:
    def __init__(self, hex_str):
        self.byte_array = bytes.fromhex(hex_str)
        self.pos = 0
        self.length = len(self.byte_array) * 8

    def __repr__(self):
        return f"BitStream(\"{self.byte_array.hex()}\")"

    def position(self):
        return self.pos

    def read(self, n):
        """Read the next _n_ bits from the stream."""
        if self.pos + n > self.length:
            raise ValueError("Not enough bits!")

        ret = 0
        while n > 0:
            i = self.pos % 8
            c = min(n, 8 - i)
            sw = 8 - c - i
            mask = 2 ** c - 1 << sw
            logging.debug(f"Reading {c} bits starting at position {self.pos} with mask {mask:#04x}")
            b = self.byte_array[self.pos // 8] & mask
            logging.debug(f"Read {b:08b}")
            logging.debug(f"ret <<= {c}")
            ret <<= c
            logging.debug(f"ret |= {b:0b} >> {sw}")
            ret |= b >> sw
            logging.debug(f"ret = {ret:0b}")
            self.pos += c
            n -= c

        logging.debug(f"Returning {ret:0b}")
        return ret

class PacketType(IntEnum):
    LITERAL = 4

class Packet:
    def __init__(self, version, type_id):
        self.version = version
        self.type_id = type_id
        
class LiteralPacket(Packet):
    def __init__(self, version, type_id, value):
        super().__init__(version, type_id)
        self.value = value

    def __eq__(self, other):
        return (
            self.version == other.version and
            self.type_id == other.type_id and
            self.value == other.value
        )
    
    def __repr__(self):
        return f"LiteralPacket({self.version}, {self.type_id}, {self.value})"

class OperatorPacket(Packet):
    def __init__(self, version, type_id, subpackets):
        super().__init__(version, type_id)
        self.subpackets = subpackets

    def __repr__(self):
        return f"OperatorPacket({self.version}, {self.type_id}, {self.subpackets})"

def decode_packets_internal(bitstream):
    start_pos = bitstream.position()

    # Extract packet version and type ID. Both of these are encoded using three
    # bits, for a total header size of 6 bits.
    version = bitstream.read(3)
    type_id = bitstream.read(3)

    logging.debug(f"Version: {version}")
    logging.debug(f"Type ID: {type_id}")

    # Switch on packet type ID to extract payload.
    if type_id == PacketType.LITERAL:
        # Extract a literal value. Literal values are always encoded in a series
        # of 5-bit groups. First, the binary representation is padded with leading
        # 0s until the length is a multiple of 4. Then, the number is broken into
        # 4 bit groups, each of which is prefixed by a 1 bit except for the last
        # group, which is prefixed with a 0.
        value = 0
        while True:
            next_group = bitstream.read(5)
            logging.debug(f"Got group: {next_group:05b}")
            value <<= 4
            value |= next_group & 0x0f
            if not next_group & 0x10:
                break
        logging.debug(f"Found literal value: {value}")
        return (
            LiteralPacket(
                version=version,
                type_id=type_id,
                value=value),
            bitstream.position() - start_pos,
        )
    else:
        # All other packet types are operators. Operators are made up of
        # subpackets. The first bit after the packet header is a flag that
        # indicates how to read the subpackets:
        #
        #   - if the flag is 0, the next 15 bits after the flag are the total
        #     length in bits of the subpackets
        #
        #   - if the flag is 1, the next 11 bits are the count of the number of
        #     subpackets.
        #
        # The subpackets begin immediately after the flag and the 15-bit or
        # 11-bit length field.
        subpackets = []
        subpackets_bits = 0
        subpackets_count = 0
        length_flag = bitstream.read(1)
        if not length_flag:
            # The next 15 bits are the total length of the subpackets, in bits.
            subpackets_bits = bitstream.read(15)
            logging.debug(f"Subpackets are {subpackets_bits} bits long.")
        else:
            # The next 11 bits are the count of the subpackets.
            subpackets_count = bitstream.read(11)
            logging.debug(f"Packet contains {subpackets_count} subpackets.")

        # Recursively decode any subpackets.
        read_count = 0
        read_bits = 0
        while (
                (length_flag and read_count < subpackets_count) or
                (not length_flag and read_bits < subpackets_bits)
        ):
            p, n = decode_packets_internal(bitstream)
            logging.debug(f"Got subpacket {p} with length {n} bits.")
            subpackets.append(p)
            read_count += 1
            read_bits += n
            
        return (
            OperatorPacket(version, type_id, subpackets),
            bitstream.position() - start_pos,
        )

def decode_packets(message):
    p, n = decode_packets_internal(BitStream(message))
    return p

def sum_packet_versions(packet):
    if packet.type_id == PacketType.LITERAL:
        return packet.version
    else:
        # This is an operator packet, sum over the subpackets.
        return packet.version + sum(map(sum_packet_versions, packet.subpackets))

def pretty_print(packet):
    def print_indented(msg, depth=0):
        spaces = " " * depth * 2
        print(f"{spaces}{msg}")
        
    def print_packet(packet, depth=0):
        if packet.type_id == PacketType.LITERAL:
            print_indented(packet, depth)
        else:
            print_indented("OperatorPacket(", depth)
            print_indented(f"{packet.version},", depth + 1)
            print_indented(f"{packet.type_id},", depth + 1)
            for subpacket in packet.subpackets:
                print_packet(subpacket, depth + 1)
            print_indented(f")", depth)
    print_packet(packet)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()
    message = args.input_file.readline().strip()
    print(f"Got input: {message}")
    packet = decode_packets(message)
    print(f"Decoded packet:")
    pretty_print(packet)
    version_sum = sum_packet_versions(packet)
    print(f"Sum of all packet versions is: {version_sum}")

if __name__ == "__main__":
    main()
