import struct
from enum import *


class TransportProtocolSegment:
    HEADER_FORMAT = "!IIBBH"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(
        self,
        seq_num,
        ack_num,
        syn=False,
        fin=False,
        ack=True,
        payload=b"",
    ):
        # I
        self.seq_num = seq_num  # Sequence Number
        # I
        self.ack_num = ack_num  # Acknowledge number
        # B
        self.syn: bool = syn  # Handshake flag
        self.fin: bool = fin  # Conection ternmination
        self.ack: bool = ack  # Acknowledge flag
        # B
        # H
        # el resto de los bytes son el payload
        self.payload = payload

    def __flags_to_int(self):
        flags = (self.syn << 7) | (self.fin << 6) | (self.ack << 5)
        return flags

    @classmethod
    def __flags_from_int(cls, flags):
        syn = bool((flags >> 7))
        fin = bool((flags >> 6) & 1)
        ack = bool((flags >> 5) & 1)
        return syn, fin, ack

    def to_bytes(self):
        flags = self.__flags_to_int()
        header = struct.pack(
            self.HEADER_FORMAT, self.seq_num, self.ack_num, flags, 0, 0
        )
        return header + self.payload

    @classmethod
    def from_bytes(cls, data):
        if len(data) < cls.HEADER_SIZE:
            raise ValueError("Segment too short")
        header = data[: cls.HEADER_SIZE]
        payload = data[cls.HEADER_SIZE :]
        seq_num, ack_num, flags, _, _ = struct.unpack(cls.HEADER_FORMAT, header)
        syn, fin, ack = cls.__flags_from_int(flags)

        return cls(seq_num, ack_num, syn, fin, ack, payload)

    def is_ack(self):
        return self.ack

    def __repr__(self):
        return (
            f"TransportProtocolSegment(seq_num={self.seq_num}, ack_num={self.ack_num}, "
            f"syn={self.syn}, fin={self.fin}, ack={self.ack}, payload={self.payload})"
        )

    @classmethod
    def create_syn(cls, seq_num):
        return cls(seq_num, 0, True, False, False, b"")

    @classmethod
    def create_syn_ack(cls, seq_num, ack_num):
        return cls(seq_num, ack_num, True, False, True, b"")

    @classmethod
    def create_fin(cls, seq_num, ack_num):
        return cls(seq_num, ack_num, False, True, False, b"")

    @classmethod
    def create_ack(cls, seq_num, ack_num):
        return cls(seq_num, ack_num, False, False, True, b"")
