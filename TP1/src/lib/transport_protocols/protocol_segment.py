from enum import *

class TransportProtocolSegment:
    HEADER_SIZE = 12

    # I I B B H
    # 4 4 1 1 2 = 12 bytes -> BIG ENDIAN

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
        header = (
            self.seq_num.to_bytes(4, byteorder="big") +
            self.ack_num.to_bytes(4, byteorder="big") +
            bytes([flags]) +
            bytes([0]) +
            (0).to_bytes(2, byteorder="big")
        )
        
        return header + self.payload

    @classmethod
    def from_bytes(cls, data):
        if len(data) < cls.HEADER_SIZE:
            raise ValueError("Segment too short")
        header = data[:cls.HEADER_SIZE]
        seq_num = int.from_bytes(header[0:4], "big")
        ack_num = int.from_bytes(header[4:8], "big")
        flags = header[8]
        syn, fin, ack = cls.__flags_from_int(flags)
        payload = data[cls.HEADER_SIZE:]
        return cls(seq_num, ack_num, syn, fin, ack, payload)

    def is_ack(self):
        return self.ack

    def is_fin(self):
        return self.fin

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
