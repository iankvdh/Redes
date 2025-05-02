from .protocol_segment import TransportProtocolSegment
import socket as skt

_START_SECUENCE_NUMBER = 0
_MAX_PAYLOAD_SIZE = 1024
_MAX_BUFFER_SIZE = 4096
_TIMEOUT_SECONDS = 2

_BYTES_FILE_SIZE = 4
_BYTES_FILE_NAME_SIZE = 2
_BYTES_IS_UPLOAD = 1

class StopAndWait:
    def __init__(self, socket: skt.socket, dest_address, msg_queue, send_queue, logger=None):
        self.timeout = _TIMEOUT_SECONDS
        self.socket: skt.socket = socket
        self.dest_address = dest_address
        self.msg_queue = msg_queue
        self.send_queue = send_queue
        self.current_seq_num = _START_SECUENCE_NUMBER
        self.logger = logger

    @classmethod
    def create_client_stop_and_wait(cls, socket, address, logger):
        return cls(socket, address, None, None, logger)

    @classmethod
    def create_server_stop_and_wait(cls, socket, address, msg_queue, send_queue ,logger):
        return cls(socket, address, msg_queue, send_queue, logger)

    def _change_seq_number(self):
        self.current_seq_num = int(not self.current_seq_num)

    ### ---------- FUNCIONES DEL CLIENTE ---------- ###

    def start_upload(self, file_name, file_size):
        self.logger.info(f"Starting upload with {file_name} and size {file_size} bytes")
        is_upload = True.to_bytes(_BYTES_IS_UPLOAD, byteorder="big")
        file_size_bytes = file_size.to_bytes(_BYTES_FILE_SIZE, byteorder="big")
        file_name_size = len(file_name.encode()).to_bytes(_BYTES_FILE_NAME_SIZE, byteorder="big")
        payload = file_size_bytes + file_name_size + is_upload + file_name.encode()
        segment = TransportProtocolSegment(
            self.current_seq_num,
            self.current_seq_num,  # en este protocolo S&W no es necesario el ACK por lo que ponemos repetido el seq_num
            False,
            False,
            False,
            payload,
        )
        data = segment.to_bytes()
        self._change_seq_number()
        self.socket.sendto(data, self.dest_address)
        while not self.wait_ack():
            self.logger.debug(
                f"Timeout waiting for ACK: {self.current_seq_num}, resending upload request"
            )
            self.socket.sendto(data, self.dest_address)

    def start_download(self, file_name):
        self.logger.info(f"Starting download with {file_name}")
        is_upload = False.to_bytes(_BYTES_IS_UPLOAD, byteorder="big")
        file_size_bytes = int(0).to_bytes(_BYTES_FILE_SIZE, byteorder="big")
        file_name_size = len(file_name.encode()).to_bytes(_BYTES_FILE_NAME_SIZE, byteorder="big")
        payload = file_size_bytes + file_name_size + is_upload + file_name.encode()
        segment = TransportProtocolSegment(
            self.current_seq_num,
            self.current_seq_num,  # en este protocolo S&W no es necesario el ACK por lo que ponemos repetido el seq_num
            False,
            False,
            False,
            payload,
        )
        data = segment.to_bytes()
        self._change_seq_number()
        self.socket.sendto(data, self.dest_address)
        while True:
            ack_received, segment = self.wait_for_ack_or_fin()
            if ack_received:
                # fin or ack
                if segment.is_fin():
                    self.logger.debug(
                        f"Received FIN for seq number {self.current_seq_num} from {self.dest_address}"
                    )
                    return False, None # avisa que el servidor no tiene el archivo

                if segment.is_ack():
                    self.logger.debug(
                        f"Received FIN for seq number {self.current_seq_num} from {self.dest_address}"
                    )
                    size_of_file = int.from_bytes(segment.payload[:4], byteorder="big")
                    return True, size_of_file # avisa que el servidor tiene el archivo y le pasa el size
            self.logger.debug(
                f"Timeout waiting for ACK: {self.current_seq_num}, resending download request"
            )
            self.socket.sendto(data, self.dest_address)

    def wait_ack(self):
        try:
            self.socket.settimeout(self.timeout)
            data, _ = self.socket.recvfrom(_MAX_BUFFER_SIZE)
            segment = TransportProtocolSegment.from_bytes(data)
            if segment.is_ack() and segment.seq_num == self.current_seq_num:
                
                self.logger.debug(
                    f"Received ACK for seq number {self.current_seq_num} from {self.dest_address}"
                )
                return True
            else:
                return False
        except skt.timeout:
            self.logger.debug(
                f"Timeout waiting for ACK: {self.current_seq_num} from {self.dest_address}"
            )
            return False
    
    def wait_for_ack_or_fin(self):
        try:
            self.socket.settimeout(self.timeout)
            data, _ = self.socket.recvfrom(_MAX_BUFFER_SIZE)
            segment = TransportProtocolSegment.from_bytes(data)
            if (segment.is_fin() or segment.is_ack()) and segment.seq_num == self.current_seq_num:
                self.logger.debug(
                    f"Received ACK for seq number {self.current_seq_num} from {self.dest_address}"
                )
                return True, segment
            else:
                return False, segment
        except skt.timeout:
            self.logger.debug(
                f"Timeout waiting for ACK: {self.current_seq_num} from {self.dest_address}"
            )
            return False, None
    
    def receive_file_from_server(self, size: int):
        data = bytearray()
        num_segments = size // _MAX_PAYLOAD_SIZE + 1
        for _ in range(num_segments):
            m_bytes, server_addr = self.socket.recvfrom(_MAX_BUFFER_SIZE)
            segment = TransportProtocolSegment.from_bytes(m_bytes)
            self._change_seq_number()
            while segment.seq_num == self.current_seq_num:
                ack_segment = TransportProtocolSegment.create_ack(
                    self.current_seq_num, self.current_seq_num
                )
                self.socket.sendto(ack_segment.to_bytes(), self.dest_address)
                self.logger.debug(
                    f"Sent ACK for seq number {self.current_seq_num} to {self.dest_address}"
                )
                m_bytes, server_addr = self.socket.recvfrom(_MAX_BUFFER_SIZE)
                segment = TransportProtocolSegment.from_bytes(m_bytes)
            data.extend(segment.payload)
            ack_segment = TransportProtocolSegment.create_ack(
                self.current_seq_num, self.current_seq_num
            )
            self.socket.sendto(ack_segment.to_bytes(), self.dest_address)
            self.logger.debug(
                f"Sent ACK for seq number {self.current_seq_num} to {self.dest_address}"
            )
        return data

    ### ---------- FUNCIONES DEL SERVIDOR ---------- ###

    def send_ack(self):
        ack_segment = TransportProtocolSegment.create_ack(
            self.current_seq_num, self.current_seq_num
        )
        self._enqueue_segment(ack_segment)
        self.logger.debug(
            f"Sent ACK for seq number {self.current_seq_num} to {self.dest_address}"
        )

    def server_wait_ack(self):
        try:
            segment = self.msg_queue.get()
            if segment.is_ack() and segment.seq_num == self.current_seq_num:
                self.logger.debug(
                    f"Received ACK for seq number {self.current_seq_num} from {self.dest_address}"
                )
                return True
            else:
                return False
        except skt.timeout:
            self.logger.debug(
                f"Timeout waiting for ACK: {self.current_seq_num} from {self.dest_address}"
            )
            return False

    def send_file_does_not_exist(self):
        self._change_seq_number()
        fin_segment = TransportProtocolSegment.create_fin(
            self.current_seq_num, self.current_seq_num
        )
        self._enqueue_segment(fin_segment)
        self.logger.debug(
            f"Sent FIN for seq number {self.current_seq_num} to {self.dest_address}"
        )
    
    def _enqueue_segment(self, segment):
        self.send_queue.put((segment, self.dest_address))
    
    def receive_file_from_client(self, size: int):
        data = bytearray()
        num_segments = size // _MAX_PAYLOAD_SIZE + 1
        # num_segments = ((size + _MAX_PAYLOAD_SIZE - 1) // _MAX_PAYLOAD_SIZE )
        for _ in range(num_segments):
            segment = self.msg_queue.get()
            self._change_seq_number()
           
            while segment.seq_num == self.current_seq_num:
                self.send_ack()
                segment = self.msg_queue.get()
            data.extend(segment.payload)
            self.send_ack()
        return data

    def receive_file_info_to_start(self):
        segment = self.msg_queue.get()
        payload = segment.payload
        file_size = int.from_bytes(payload[:4], byteorder="big")
        file_name_size = int.from_bytes(payload[4:6], byteorder="big")
        is_upload = bool.from_bytes(payload[6:7], byteorder="big")
        file_name = payload[7 : 7 + file_name_size].decode()
        if is_upload:
            self._change_seq_number()
            self.send_ack()
        # si es download, luego otra función (send_file_size_to_client) enviará el ack y en el payload, el file_size
        return file_size, file_name, is_upload        

    def send_file_size_to_client(self, file_size):
        file_size_bytes = file_size.to_bytes(4, byteorder="big")
        payload = file_size_bytes
        self._change_seq_number()
        segment = TransportProtocolSegment(
            self.current_seq_num,
            self.current_seq_num,
            False,
            False,
            True,
            payload,
        )
        self._enqueue_segment(segment)
        
    def send_client_file_to_server(self, data: bytes):
        num_segments = len(data) // _MAX_PAYLOAD_SIZE + 1
        for i in range(num_segments):
            start = i * _MAX_PAYLOAD_SIZE
            end = min(start + _MAX_PAYLOAD_SIZE, len(data))
            payload = data[start:end]
            segment = TransportProtocolSegment(
                self.current_seq_num,
                self.current_seq_num,
                False,
                False,
                False,
                payload,
            )
            data = segment.to_bytes()
            self._change_seq_number()
            self.socket.sendto(data, self.dest_address)
            while not self.wait_ack():
                self.socket.sendto(data, self.dest_address)

    def send_server_file_to_client(self, data: bytes):
        num_segments = len(data) // _MAX_PAYLOAD_SIZE + 1
        for i in range(num_segments):
            start = i * _MAX_PAYLOAD_SIZE
            end = min(start + _MAX_PAYLOAD_SIZE, len(data))
            payload = data[start:end]
            segment = TransportProtocolSegment(
                self.current_seq_num,
                self.current_seq_num,
                False,
                False,
                False,
                payload,
            )
            self._change_seq_number()
            self._enqueue_segment(segment)
            while not self.server_wait_ack():
                self._enqueue_segment(segment)
