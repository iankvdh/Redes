import struct

class TransportProtocolSegment:
    HEADER_FORMAT = "!IIBBH"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, seq_num, ack_num, syn=False, fin=False, ack=True, upload=False, payload=b''):
        self.seq_num = seq_num # Sequence Number
        self.ack_num = ack_num # Acknowledge number
        self.syn : bool = syn # Handshake flag
        self.fin : bool = fin # Conection ternmination
        self.ack : bool = ack # Acknowledge flag
        self.upload : bool = upload # "The client wants to upload a file" flag
        self.payload = payload
    
    def __flags_to_int(self):
        flags = (self.syn << 7) | (self.fin << 6) | (self.ack << 5) | (self.upload << 4)
        return flags

    @classmethod
    def __flags_from_int(cls, flags):
        syn = bool((flags >> 7))
        fin = bool((flags >> 6) & 1)
        ack = bool((flags >> 5) & 1)
        upload = bool((flags >> 4) & 1)
        return syn, fin, ack, upload    

    def to_bytes(self):
        flags = self.__flags_to_int()
        header = struct.pack(self.HEADER_FORMAT, self.seq_num, self.ack_num, flags)
        return header + self.payload

    @classmethod
    def from_bytes(cls, data):
        if len(data) < cls.HEADER_SIZE:
            raise ValueError("Segment too short")
        header = data[:cls.HEADER_SIZE]
        payload = data[cls.HEADER_SIZE:]
        seq_num, ack_num, flags = struct.unpack(cls.HEADER_FORMAT, header)
        syn, fin, ack, upload = cls.__flags_from_int(flags)
        
        return cls(seq_num, ack_num, syn, fin, ack, upload, payload)

    def __repr__(self):
        return f"<TransportProtocolSegment seq={self.seq_num} ack={self.ack_num} flags={self.flags} payload_len={len(self.payload)}>"

    @classmethod
    def create_syn(cls, seq_num, upload):
        return cls(seq_num, 0, True, False, False, upload, b'')
    
    @classmethod
    def create_syn_ack(cls, seq_num, ack_num, upload):
        return cls(seq_num, ack_num, True, False, True, upload, b'')

    @classmethod
    def create_fin(cls, seq_num, ack_num, upload):
        return cls(seq_num, ack_num, False, True, False, upload, b'')
    
    @classmethod
    def create_ack(cls, seq_num, ack_num, upload):
        return cls(seq_num, ack_num, False, False, True, upload, b'')