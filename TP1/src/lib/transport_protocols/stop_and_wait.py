from .protocol_segment import TransportProtocolSegment
import socket as skt
import time

_START_SECUENCE_NUMBER = 0
# _START_ACK_NUMBER = 0
_MAX_PAYLOAD_SIZE = 1024
_MAX_BUFFER_SIZE = 4096
_TIMEOUT_SECONDS = 2


class StopAndWait:
    def __init__(self, socket: skt.socket, dest_address, msg_queue, logger=None):
        self.timeout = _TIMEOUT_SECONDS
        self.socket: skt.socket = socket
        self.dest_address = dest_address
        self.msg_queue = msg_queue
        self.current_seq_num = _START_SECUENCE_NUMBER
        self.logger = logger
        # self.current_ack_num = _START_ACK_NUMBER

    @classmethod
    def create_client_stop_and_wait(cls, socket, address, logger):
        return cls(socket, address, None, logger)

    @classmethod
    def create_server_stop_and_wait(cls, socket, address, msg_queue):
        return cls(socket, address, msg_queue)

    def _change_seq_number(self):
        self.current_seq_num = int(not self.current_seq_num)

    # def _change_ack_number(self):
    #     self.current_ack_num += 1

    def start_upload(self, file_name, file_size):

        print(f"Starting upload with {file_name} and size {file_size} bytes")
        self.logger.info(f"Starting upload with {file_name} and size {file_size} bytes")
        is_upload = True.to_bytes(byteorder="big")
        # convertir file_size en bytes big-endian
        file_size_bytes = file_size.to_bytes(4, byteorder="big")
        # enviar nombre de archivo y tamaño
        file_name_size = len(file_name.encode()).to_bytes(2, byteorder="big")
        payload = file_size_bytes + file_name_size + is_upload + file_name.encode()

        # payload = file_size_bytes + b"\0" + file_name.encode() + b"\0" + is_upload
        # creo segmento de transporte
        segment = TransportProtocolSegment(
            self.current_seq_num,
            self.current_seq_num,  # en este protocolo S&W no es necesario el ACK por lo que ponemos repetido el seq_num
            False,
            False,
            False,
            payload,
        )
        # lo convierto a bytes
        data = segment.to_bytes()
        # lo envio
        self._change_seq_number()  # el primer segmento que se envia es el 1
        self.socket.sendto(data, self.dest_address)
        while not self.wait_ack():
            self.logger.debug(
                f"Timeout waiting for ACK: {self.current_seq_num}, resending upload request"
            )
            self.socket.sendto(data, self.dest_address)
        # print(f"Sent upload request to {self.dest_address}")
        # print(f"AHORA MI NUM_SEQ ES {self.current_seq_num}")

    def start_download(self, file_name):
        pass

    def send_ack(self):
        ack_segment = TransportProtocolSegment.create_ack(
            self.current_seq_num, self.current_seq_num
        )
        data = ack_segment.to_bytes()
        self.socket.sendto(data, self.dest_address)
        self.logger.debug(
            f"Sent ACK for seq number {self.current_seq_num} to {self.dest_address}"
        )
        # print(f"Sent ACK for seq number {self.current_ack_num}")
        time.sleep(0.5)  # Esperar un poco para asegurar que el ACK se envíe

    def wait_ack(self):
        try:
            self.socket.settimeout(self.timeout)
            data, _ = self.socket.recvfrom(_MAX_BUFFER_SIZE)

            # Intentamos reconstruir el segmento (que tendrá el flag de ACK prendido)
            segment = TransportProtocolSegment.from_bytes(data)

            if segment.is_ack() and segment.seq_num == self.current_seq_num:
                self.logger.debug(
                    f"Received ACK for seq number {self.current_seq_num} from {self.dest_address}"
                )
                # self._change_ack_number()  # ack del cliente
                return True

            else:
                return False

        except skt.timeout:
            print(f"Timeout waiting for ACK: {self.current_seq_num}")
            self.logger.debug(
                f"Timeout waiting for ACK: {self.current_seq_num} from {self.dest_address}"
            )
            return False

    def send(self, data: bytes):
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
            print(f"ENVIO SEQ_NUM = {self.current_seq_num}")
            self.socket.sendto(data, self.dest_address)
            while not self.wait_ack():
                # verificar si hay que manejar intentos maximos (retries)
                self.socket.sendto(data, self.dest_address)

    def receive(self, size: int):
        data = bytearray()
        num_segments = size // _MAX_PAYLOAD_SIZE + 1
        for _ in range(num_segments):
            segment = self.msg_queue.get()

            self._change_seq_number()
            while segment.seq_num == self.current_seq_num:
                self.send_ack()
                segment = self.msg_queue.get()

            data.extend(segment.payload)
            print(f"ENVIO ACK AL CLIENTE CON NUMERO  receive = {self.current_seq_num}")
            self.send_ack()

        return data

    def receive_file_info(self):
        # Recibo el nombre del archivo y su tamaño
        segment = self.msg_queue.get()

        payload = segment.payload
        file_size = int.from_bytes(payload[:4], byteorder="big")
        file_name_size = int.from_bytes(payload[4:6], byteorder="big")
        is_upload = bool.from_bytes(payload[6:7], byteorder="big")
        file_name = payload[7 : 7 + file_name_size].decode()

        self._change_seq_number()
        print(
            f"ENVIO ACK AL CLIENTE CON NUMERO  receive_file_info = {self.current_seq_num}"
        )
        self.send_ack()

        return file_size, file_name, is_upload
