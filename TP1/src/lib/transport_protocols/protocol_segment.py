from ..constants import HEADER_SIZE


class TransportProtocolSegment:
    """
    I (4 bytes)  -> seq_num
    B (1 byte)   -> flags (solo usaremos fin y ack)
    B (1 byte)   -> padding
    H (2 bytes)  -> padding
    -> TOTAL: 8 bytes
    """

    def __init__(
        self,
        seq_num,
        fin=False,
        ack=True,
        payload=b"",
    ):
        self.seq_num = seq_num  # Sequence Number
        self.fin: bool = fin  # Conection ternmination
        self.ack: bool = ack  # Acknowledge flag
        # el resto de los bytes son el payload
        self.payload = payload

    def __flags_to_int(self):
        flags = (self.fin << 6) | (self.ack << 5)
        return flags

    @classmethod
    def __flags_from_int(cls, flags):
        fin = bool((flags >> 6) & 1)
        ack = bool((flags >> 5) & 1)
        return fin, ack

    def to_bytes(self):
        flags = self.__flags_to_int()
        header = (
            self.seq_num.to_bytes(4, byteorder="big")
            + bytes([flags])
            + bytes([0])
            + (0).to_bytes(2, byteorder="big")
        )
        return header + self.payload

    @classmethod
    def from_bytes(cls, data):
        if len(data) < HEADER_SIZE:
            raise ValueError("Segment too short")
        header = data[:HEADER_SIZE]
        seq_num = int.from_bytes(header[0:4], "big")
        flags = header[4]
        fin, ack = cls.__flags_from_int(flags)
        payload = data[HEADER_SIZE:]
        return cls(seq_num, fin, ack, payload)

    def is_ack(self):
        return self.ack

    def is_fin(self):
        return self.fin

    def __repr__(self):
        return (
            f"TransportProtocolSegment(seq_num={self.seq_num}"
            f"fin={self.fin}, ack={self.ack}, payload={self.payload})"
        )

    @classmethod
    def create_fin(cls, seq_num):
        return cls(seq_num, True, False, b"")

    @classmethod
    def create_ack(cls, seq_num):
        return cls(seq_num, False, True, b"")
