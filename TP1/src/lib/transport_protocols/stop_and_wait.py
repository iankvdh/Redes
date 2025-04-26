from .protocol_segment import TransportProtocolSegment
import socket as skt

_START_SECUENCE_NUMBER = 0
_START_ACK_NUMBER = 0
_MAX_PAYLOAD_SIZE = 1024
_MAX_BUFFER_SIZE = 4096
_TIMEOUT_SECONDS = 2


class StopAndWait:
    def __init__(self, socket: skt.socket, dest_address, msg_queue):
        self.timeout = _TIMEOUT_SECONDS
        self.socket: skt.socket = socket
        self.dest_address = dest_address
        self.msg_queue = msg_queue
        self.current_seq_num = _START_SECUENCE_NUMBER
        self.current_ack_num = _START_ACK_NUMBER

    @classmethod
    def create_client_stop_and_wait(cls, socket, address):
        return cls(socket, address, None)

    @classmethod
    def create_server_stop_and_wait(cls, socket, address, msg_queue):
        return cls(socket, address, msg_queue)

    def _change_seq_number(self):
        self.current_seq_num = int(not self.current_seq_num)

    def _change_ack_number(self):
        self.current_ack_num = int(not self.current_ack_num)

    def start_upload(self, file_name, file_size):
        print(f"Starting upload with {file_name} and size {file_size} bytes")
        is_upload = True.to_bytes(byteorder="big")
        # convertir file_size en bytes big-endian
        file_size_bytes = file_size.to_bytes(4, byteorder="big")
        # enviar nombre de archivo y tamaño
        payload = file_size_bytes + b"\0" + file_name.encode() + b"\0" + is_upload
        for b in payload:
            print(chr(b), end="")
        print("\n")
        # creo segmento de transporte
        segment = TransportProtocolSegment(
            self.current_seq_num,
            self.current_ack_num,
            False,
            False,
            False,
            payload,
        )
        # lo convierto a bytes
        data = segment.to_bytes()
        # lo envio
        self.socket.sendto(data, self.dest_address)
        while not self.wait_ack():
            self.socket.sendto(data, self.dest_address)
        print(f"Sent upload request to {self.dest_address}")
        self._change_seq_number()

    def start_download(self, file_name):
        pass

    def send_ack(self):
        ack_segment = TransportProtocolSegment.create_ack(
            self.current_seq_num, self.current_ack_num
        )
        data = ack_segment.to_bytes()
        self.socket.sendto(data, self.dest_address)
        print(f"Sent ACK for seq number {self.current_seq_num}")

    def wait_ack(self):
        try:
            self.socket.settimeout(self.timeout)
            data, _ = self.socket.recvfrom(_MAX_BUFFER_SIZE)

            # Intentamos reconstruir el segmento (que tendrá el flag de ACK prendido)
            segment = TransportProtocolSegment.from_bytes(data)

            if segment.is_ack() and segment.seq_num == self._next_expected_ack_number():
                print(f"Received ACK for seq number {self.current_ack_num}")
                self._change_ack_number()
                return True

            else:
                print(
                    f"Received unexpected segment or wrong ACK.Expected {self.current_ack_num}, got {segment.ack_num}"
                )
                return False

        except skt.timeout:
            print(f"Timeout waiting for ACK: {self.current_ack_num}")
            return False

    def send(self, data: bytes):
        num_segments = len(data) // _MAX_PAYLOAD_SIZE + 1
        for i in range(num_segments):
            start = i * _MAX_PAYLOAD_SIZE
            end = max(start + _MAX_PAYLOAD_SIZE, len(data))
            payload = data[start:end]
            segment = TransportProtocolSegment(
                self.current_seq_num,
                self.current_ack_num,
                False,
                False,
                False,
                True,
                payload,
            )
            data = segment.to_bytes()
            self.socket.sendto(data, self.dest_address)
            while (
                not self.wait_ack()
            ):  # verificar si hay que manejar intentos maximos (retries)
                self.socket.sendto(data, self.dest_address)
            self._change_seq_number()

    def receive(self, size: int):
        data = bytearray()
        num_segments = size // _MAX_PAYLOAD_SIZE + 1
        for _ in range(num_segments):
            segment = self.msg_queue.get()

            while segment.seq_num != self._next_expected_ack_number():
                self.send_ack()
                segment = self.msg_queue.get()

            data.extend(segment.payload)
            self._change_ack_number()
            self.send_ack()

        return data

    def _next_expected_ack_number(self):
        return int(not self.current_ack_num)

    def receive_file_info(self):
        # Recibo el nombre del archivo y su tamaño
        segment = self.msg_queue.get()
        file_size, file_name, is_upload = segment.payload.split(
            b"\0", maxsplit=2
        )  # el maxsplit=2 es por el \0 que está en el string de filename
        file_size = int.from_bytes(file_size, byteorder="big")
        is_upload = bool.from_bytes(is_upload, byteorder="big")
        print(f"file_size = {file_size}")
        print(f"is_upload = {is_upload}")
        return file_size, file_name.decode(), is_upload
