
from .protocol_segment import TransportProtocolSegment
import socket as skt
import time
import threading

_WINDOW_SIZE = 4
_START_SECUENCE_NUMBER = 0
_START_ACK_NUMBER = 0
_MAX_PAYLOAD_SIZE = 1024
_MAX_BUFFER_SIZE = 4096
_TIMEOUT_SECONDS = 0.1


_BYTES_FILE_SIZE = 4
_BYTES_FILE_NAME_SIZE = 2
_BYTES_IS_UPLOAD = 1


class SelectiveRepeat:
    def __init__(self, socket, address, msg_queue, send_queue, logger=None):
        self.timeout = _TIMEOUT_SECONDS
        self.socket = socket
        self.msg_queue = msg_queue # queue que usa el server para recibir del cliente
        self.send_queue = send_queue # queue que usa el server para enviar al cliente
        self.dest_address = address
        # self.current_seq_num = _START_SECUENCE_NUMBER
        # self.current_ack_num = _START_ACK_NUMBER
        self.logger = logger
        self.window_size = _WINDOW_SIZE

        # Estado de ventana
        self.send_base = _START_SECUENCE_NUMBER
        self.next_seq_num = _START_SECUENCE_NUMBER
        self.recv_base = _START_SECUENCE_NUMBER

        # Buffers
        self.send_buffer = {}  # seq_num -> (segment_bytes, time_sent)
        self.recv_buffer = {}  # seq_num -> segment

        self.ack_received = set()  # seq_nums ya ACKeados

        # Lock para concurrencia
        self.lock = threading.Lock()

        # Hilo para retransmisiones
        self.running = True
        self.retransmission_thread = threading.Thread(target=self._retransmit_timer)
        self.retransmission_thread.start()


    @classmethod
    def create_client_selective_repeat(cls, socket, address, logger):
        return cls(socket, address, None, None, logger)
    
    @classmethod
    def create_server_selective_repeat(cls, socket, address, msg_queue, send_queue, logger):
        return cls(socket, address, msg_queue, send_queue, logger)
    
    def _in_window(self, seq_num, base): # cuando llegue algun segmento se llama esta funcion (tanto en el cliente como en el server)   
        """
        CLIENT: 
            base = ppio de la ventana -> más viejo ack
            seq_num = # ACK que recibe
        SERVER:
            base =  ppio de la ventana -> más viejo ack 
            seq_num = # ACK que recibe
        """
        return base <= seq_num < base + _WINDOW_SIZE

    def _retransmit_timer(self):
        while self.running:
            now = time.time()
            with self.lock:
                for seq_num in list(self.send_buffer):
                    segment_bytes, time_sent = self.send_buffer[seq_num]
                    if now - time_sent > self.timeout:
                        self.socket.sendto(segment_bytes, self.dest_address)
                        self.send_buffer[seq_num] = (segment_bytes, time.time())
                        self.logger.debug(f"Retransmitted seq {seq_num}")
            time.sleep(0.1)  # Sleep pequeño para no consumir CPU

    def stop(self): 
        """
        TODO
        CLIENT: Cuando termina de recibir los paquetes y finaliza su operacion / (en el close del cliente)
        USER_MANAGER: Cuando el cliente asociado termina su operacion / (en el close del user_mager)
        SERVER: Cuando tira su propio "exit" y llame al stop del user_manager / (en el close del server)
        """
        self.running = False
        self.retransmission_thread.join()

    ### ---------- FUNCIONES DEL CLIENTE ---------- ###

    def start_upload(self, file_name, file_size):
        self.logger.info(f"Starting upload with {file_name} and size {file_size} bytes")
        is_upload = True.to_bytes(_BYTES_IS_UPLOAD, byteorder="big")
        file_size_bytes = file_size.to_bytes(_BYTES_FILE_SIZE, byteorder="big")
        file_name_size = len(file_name.encode()).to_bytes(_BYTES_FILE_NAME_SIZE, byteorder="big")
        payload = file_size_bytes + file_name_size + is_upload + file_name.encode()
        segment = TransportProtocolSegment(
            self.next_seq_num,
            self.next_seq_num,
            False,
            False,
            False,
            payload,
        )
        data = segment.to_bytes()

        with self.lock:
            self.socket.sendto(data, self.dest_address)
            self.send_buffer[self.next_seq_num] = (data, time.time()) 
            # el paquete enviado, se guarda en {paq,enviados} con el tiempo actual al enviarse
            self.next_seq_num += 1
    
        # overlogic ?
        # while self.next_seq_num - self.send_base >= _WINDOW_SIZE or not self.wait_ack():
        #     self.logger.debug(f"Waiting for ACKs in upload window")
        while not self.wait_ack():
            self.logger.debug(f"Waiting for ACKs in upload window")
            


    def start_download(self, file_name):
        self.logger.info(f"Starting download with {file_name}")
        is_upload = False.to_bytes(_BYTES_IS_UPLOAD, byteorder="big")
        file_size_bytes = int(0).to_bytes(_BYTES_FILE_SIZE, byteorder="big")
        file_name_size = len(file_name.encode()).to_bytes(_BYTES_FILE_NAME_SIZE, byteorder="big")
        payload = file_size_bytes + file_name_size + is_upload + file_name.encode()
        segment = TransportProtocolSegment(
            self.next_seq_num,
            self.next_seq_num,
            False,
            False,
            False,
            payload,
        )
        data = segment.to_bytes()

        with self.lock:
            self.socket.sendto(data, self.dest_address)
            self.send_buffer[self.next_seq_num] = (data, time.time())
            self.next_seq_num += 1

        while True:
            ack_received, segment = self.wait_for_ack_or_fin()
            # recv_base = 0 ####
            self.recv_base += 1 
            if ack_received:
                if segment.is_fin():
                    return False, None
                if segment.is_ack():
                    size_of_file = int.from_bytes(segment.payload[:4], byteorder="big")
                    
                    return True, size_of_file

    def wait_ack(self):
        try:
            self.socket.settimeout(self.timeout)
            data, _ = self.socket.recvfrom(_MAX_BUFFER_SIZE)
            segment = TransportProtocolSegment.from_bytes(data)
            with self.lock:
                # agrego el ack que recibi
                # (for security: chequear que el que se reciba este dentro de la ventana -> no me puede llegar uno que no este esperando -> ej: [0, 1, 2, 3] y de la nada recibo un 8 .-. )
                self.ack_received.add(segment.seq_num)
                if segment.seq_num in self.send_buffer:
                    del self.send_buffer[segment.seq_num]
                while self.send_base in self.ack_received:
                    self.send_base += 1
                return True
        except skt.timeout:
            return False

    def wait_for_ack_or_fin(self):
        try:
            self.socket.settimeout(self.timeout)
            data, _ = self.socket.recvfrom(_MAX_BUFFER_SIZE)
            segment = TransportProtocolSegment.from_bytes(data)
            with self.lock:
                self.ack_received.add(segment.seq_num)
                if segment.seq_num in self.send_buffer:
                    del self.send_buffer[segment.seq_num]
                while self.send_base in self.ack_received:
                    self.send_base += 1
                return True, segment
        except skt.timeout:
            return False, None

    def receive_file_from_server(self, size: int):
        data = bytearray()
        
        while len(data) < size:
            m_bytes, _ = self.socket.recvfrom(_MAX_BUFFER_SIZE)
            segment = TransportProtocolSegment.from_bytes(m_bytes)

            seq_num = segment.seq_num
            
            if self._in_window(seq_num, self.recv_base):
                self.recv_buffer[seq_num] = segment

                # ACK siempre
                ack_segment = TransportProtocolSegment.create_ack(seq_num, seq_num)
                self.socket.sendto(ack_segment.to_bytes(), self.dest_address)

                self.logger.debug(f"ACK sent for seq {seq_num}")

                # Avanzamos recv_base si tenemos en orden
                while self.recv_base in self.recv_buffer:
                    in_order_segment = self.recv_buffer.pop(self.recv_base)
                    data.extend(in_order_segment.payload)
                    self.recv_base += 1

        return data[:size]

    ### ---------- FUNCIONES DEL SERVIDOR ---------- ###

    def send_ack(self, seq_num):
        ack_segment = TransportProtocolSegment.create_ack(seq_num, seq_num)
        self._enqueue_segment(ack_segment)


    def server_wait_ack(self):
        try:
            segment = self.msg_queue.get()
            with self.lock:
                self.ack_received.add(segment.seq_num)
                if segment.seq_num in self.send_buffer:
                    del self.send_buffer[segment.seq_num]
                while self.send_base in self.ack_received:
                    self.send_base += 1
                return True
        except skt.timeout:
            return False

    def send_file_does_not_exist(self):
        fin_segment = TransportProtocolSegment.create_fin(
            self.next_seq_num, self.next_seq_num
        )
        self._enqueue_segment(fin_segment)
        self.next_seq_num += 1

    def _enqueue_segment(self, segment):
        self.send_queue.put((segment, self.dest_address))

    def receive_file_from_client(self, size: int):
        # size = 48
        data = bytearray()
        expected_num_segments = size // _MAX_PAYLOAD_SIZE + 1

        while len(data) < size:
            segment = self.msg_queue.get()
            self.logger.debug(f"Received segment with seq_num {segment.seq_num} and payload size {len(segment.payload)}")
            if self._in_window(segment.seq_num, self.recv_base):
                self.recv_buffer[segment.seq_num] = segment
                self.send_ack(segment.seq_num)

                while self.recv_base in self.recv_buffer:
                    in_order_segment = self.recv_buffer.pop(self.recv_base)
                    data.extend(in_order_segment.payload)
                    self.recv_base += 1
            elif segment.seq_num < self.recv_base:
                self.send_ack(segment.seq_num)
        return data[:size]

    def receive_file_info_to_start(self):
        segment = self.msg_queue.get()
        payload = segment.payload
        file_size = int.from_bytes(payload[:4], byteorder="big")
        file_name_size = int.from_bytes(payload[4:6], byteorder="big")
        is_upload = bool.from_bytes(payload[6:7], byteorder="big")
        file_name = payload[7 : 7 + file_name_size].decode()
        if is_upload:
            self.send_ack(segment.seq_num) # GOD (posible mejora para stop and wait)
        self.recv_base += 1  
        return file_size, file_name, is_upload

    def send_file_size_to_client(self, file_size):
        file_size_bytes = file_size.to_bytes(4, byteorder="big")
        payload = file_size_bytes
        segment = TransportProtocolSegment(
            self.next_seq_num,
            self.next_seq_num,
            False,
            False,
            True,
            payload,
        )
        self._enqueue_segment(segment)
        self.send_base += 1
        self.next_seq_num += 1

    def send_client_file_to_server(self, data: bytes):
        num_segments = len(data) // _MAX_PAYLOAD_SIZE + 1

        i = 0
        while i < num_segments:
            with self.lock:
                if self.next_seq_num - self.send_base < _WINDOW_SIZE:
                    start = i * _MAX_PAYLOAD_SIZE
                    end = min(start + _MAX_PAYLOAD_SIZE, len(data))
                    payload = data[start:end]

                    segment = TransportProtocolSegment(
                        self.next_seq_num,
                        self.next_seq_num,
                        False,
                        False,
                        False,
                        payload,
                    )
                    segment_bytes = segment.to_bytes()
                    self.socket.sendto(segment_bytes, self.dest_address)

                    self.send_buffer[self.next_seq_num] = (segment_bytes, time.time())
                    self.next_seq_num += 1
                    i += 1

            self.wait_ack()

    def send_server_file_to_client(self, data: bytes):
        num_segments = len(data) // _MAX_PAYLOAD_SIZE + 1

        i = 0
        while i < num_segments:
            with self.lock:
                if self.next_seq_num - self.send_base < _WINDOW_SIZE:
                    start = i * _MAX_PAYLOAD_SIZE
                    end = min(start + _MAX_PAYLOAD_SIZE, len(data))
                    payload = data[start:end]

                    segment = TransportProtocolSegment(
                        self.next_seq_num,
                        self.next_seq_num,
                        False,
                        False,
                        False,
                        payload,
                    )
                    self._enqueue_segment(segment)

                    segment_bytes = segment.to_bytes()
                    self.send_buffer[self.next_seq_num] = (segment_bytes, time.time())
                    self.next_seq_num += 1
                    i += 1

            self.server_wait_ack()
