import time
from .protocol_segment import TransportProtocolSegment
import socket as skt
from queue import Empty
from lib.constants import (
    START_SECUENCE_NUMBER,
    MAX_PAYLOAD_SIZE,
    MAX_SEGMENT_SIZE,
    TIMEOUT_SECONDS,
    RETRANSMIT_TIMER,
    BYTES_FILE_SIZE,
    BYTES_FILE_NAME_SIZE,
    BYTES_IS_UPLOAD,
    NUM_FIN_SEGMENTS_TO_SEND,
)


class StopAndWait:
    def __init__(
        self, socket: skt.socket, dest_address, msg_queue, send_queue, logger=None
    ):
        self.timeout = TIMEOUT_SECONDS
        self.socket: skt.socket = socket
        self.dest_address = dest_address
        self.msg_queue = msg_queue
        self.send_queue = send_queue
        self.current_seq_num = START_SECUENCE_NUMBER
        self.logger = logger

    @classmethod
    def create_client_stop_and_wait(cls, socket, address, logger):
        return cls(socket, address, None, None, logger)

    @classmethod
    def create_server_stop_and_wait(
        cls, socket, address, msg_queue, send_queue, logger
    ):
        return cls(socket, address, msg_queue, send_queue, logger)

    def _change_seq_number(self):
        self.current_seq_num += 1

    def stop(self):
        self.logger.debug("Protocol stopped: connection closed with another host.")

    # ---------- FUNCIONES DEL CLIENTE ---------- #

    def start_upload(self, file_name, file_size):
        self.logger.info(
            f"Starting upload with {file_name} and size {file_size} bytes."
        )
        is_upload = True.to_bytes(BYTES_IS_UPLOAD, byteorder="big")
        file_size_bytes = file_size.to_bytes(BYTES_FILE_SIZE, byteorder="big")
        file_name_size = len(file_name.encode()).to_bytes(
            BYTES_FILE_NAME_SIZE, byteorder="big"
        )
        payload = file_size_bytes + file_name_size + is_upload + file_name.encode()
        segment = TransportProtocolSegment(
            self.current_seq_num,
            False,
            False,
            payload,
        )
        data = segment.to_bytes()
        self.socket.sendto(data, self.dest_address)
        while not self.wait_ack():
            self.logger.debug(
                f"Timeout waiting for ACK: {self.current_seq_num}, resending upload request"
            )
            self.socket.sendto(data, self.dest_address)
        self._change_seq_number()

    def start_download(self, file_name):
        self.logger.info(f"Starting download with {file_name}.")
        is_upload = False.to_bytes(BYTES_IS_UPLOAD, byteorder="big")
        file_size_bytes = int(0).to_bytes(BYTES_FILE_SIZE, byteorder="big")
        file_name_size = len(file_name.encode()).to_bytes(
            BYTES_FILE_NAME_SIZE, byteorder="big"
        )
        payload = file_size_bytes + file_name_size + is_upload + file_name.encode()
        segment = TransportProtocolSegment(
            self.current_seq_num,
            False,
            False,
            payload,
        )
        data = segment.to_bytes()
        self.socket.sendto(data, self.dest_address)
        while True:
            ack_received, segment = self.wait_for_ack_or_fin()
            if ack_received:
                # fin or ack
                if segment.is_fin():
                    self.logger.debug(
                        f"Received FIN for seq number {self.current_seq_num} from {self.dest_address}"
                    )
                    self._change_seq_number()
                    return False, None  # avisa que el servidor no tiene el archivo

                if segment.is_ack():
                    self.logger.debug(
                        f"Received ACK for seq number {self.current_seq_num} from {self.dest_address}"
                    )
                    size_of_file = int.from_bytes(segment.payload[:4], byteorder="big")
                    ack_segment = TransportProtocolSegment.create_ack(
                        self.current_seq_num
                    )
                    self.socket.sendto(ack_segment.to_bytes(), self.dest_address)
                    self.logger.debug(f"ACK sent for seq {self.current_seq_num}")
                    self._change_seq_number()
                    return (
                        True,
                        size_of_file,
                    )  # avisa que el servidor tiene el archivo y le pasa el size
            self.logger.debug(
                f"Timeout waiting for ACK: {self.current_seq_num}, resending download request"
            )
            self.socket.sendto(data, self.dest_address)

    def wait_ack(self):
        try:
            self.socket.settimeout(self.timeout)
            data, _ = self.socket.recvfrom(MAX_SEGMENT_SIZE)
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
        finally:
            self.socket.settimeout(None)

    def wait_for_ack_or_fin(self):
        try:
            self.socket.settimeout(self.timeout)
            data, _ = self.socket.recvfrom(MAX_SEGMENT_SIZE)
            segment = TransportProtocolSegment.from_bytes(data)
            if segment.is_fin() or (
                segment.is_ack() and segment.seq_num == self.current_seq_num
            ):
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
        finally:
            self.socket.settimeout(None)

    def receive_file_from_server(self, size: int):
        data = bytearray()
        num_segments = size // MAX_PAYLOAD_SIZE + 1
        for _ in range(num_segments):
            m_bytes, server_addr = self.socket.recvfrom(MAX_SEGMENT_SIZE)
            segment = TransportProtocolSegment.from_bytes(m_bytes)
            while segment.seq_num != self.current_seq_num:
                ack_segment = TransportProtocolSegment.create_ack(segment.seq_num)
                self.socket.sendto(ack_segment.to_bytes(), self.dest_address)
                self.logger.debug(
                    f"Sent ACK for seq number {self.current_seq_num} to {self.dest_address}"
                )
                m_bytes, server_addr = self.socket.recvfrom(MAX_SEGMENT_SIZE)
                segment = TransportProtocolSegment.from_bytes(m_bytes)
            data.extend(segment.payload)
            ack_segment = TransportProtocolSegment.create_ack(segment.seq_num)
            self.socket.sendto(ack_segment.to_bytes(), self.dest_address)
            self.logger.debug(
                f"Sent ACK for seq number {self.current_seq_num} to {self.dest_address}"
            )
            self._change_seq_number()
        return data

    # ---------- FUNCIONES DEL SERVIDOR ---------- #

    def send_ack(self, seq_num):

        ack_segment = TransportProtocolSegment.create_ack(seq_num)
        self._enqueue_segment(ack_segment)
        self.logger.debug(f"Sent ACK for seq number {seq_num} to {self.dest_address}")

    def server_wait_ack(self):
        try:
            segment = self.msg_queue.get(timeout=TIMEOUT_SECONDS)
            if segment.is_fin() or (
                segment.is_ack() and segment.seq_num == self.current_seq_num
            ):
                self.logger.debug(
                    f"Received ACK for seq number {self.current_seq_num} from {self.dest_address}"
                )
                return True, segment
            else:
                return False, segment
        except Empty:
            self.logger.debug(
                f"Timeout waiting for ACK: {self.current_seq_num} from {self.dest_address}"
            )
            return False, None

    def send_file_does_not_exist(self):
        self._change_seq_number()
        fin_segment = TransportProtocolSegment.create_fin(self.current_seq_num)
        self._enqueue_segment(fin_segment)
        self.logger.debug(
            f"Sent FIN for seq number {self.current_seq_num} to {self.dest_address}"
        )

    def _enqueue_segment(self, segment):
        self.send_queue.put((segment, self.dest_address))

    def receive_file_from_client(self, size: int):
        data = bytearray()
        num_segments = size // MAX_PAYLOAD_SIZE + 1
        for _ in range(num_segments):
            segment = self.msg_queue.get()

            while segment.seq_num != self.current_seq_num:
                self.send_ack(segment.seq_num)
                segment = self.msg_queue.get()
            data.extend(segment.payload)
            self.send_ack(segment.seq_num)
            self._change_seq_number()

        return data

    def receive_file_info_to_start(self):
        segment = self.msg_queue.get()
        payload = segment.payload
        file_size = int.from_bytes(payload[:4], byteorder="big")
        file_name_size = int.from_bytes(payload[4:6], byteorder="big")
        is_upload = bool.from_bytes(payload[6:7], byteorder="big")
        file_name = payload[7 : 7 + file_name_size].decode()
        if is_upload:
            self.send_ack(segment.seq_num)
            self._change_seq_number()
        # si es download, luego otra función (send_file_size_to_client)
        # enviará el ack y en el payload, el file_size
        return file_size, file_name, is_upload

    def send_file_size_to_client(self, file_size):
        file_size_bytes = file_size.to_bytes(4, byteorder="big")
        payload = file_size_bytes
        segment = TransportProtocolSegment(
            self.current_seq_num,
            False,
            True,
            payload,
        )
        self._enqueue_segment(segment)
        while not self.server_wait_ack()[0]:
            self.logger.debug("Waiting for file size ACK")
            self._enqueue_segment(segment)
        self._change_seq_number()

    def send_client_file_to_server(self, data: bytes):
        # num_segments = len(data) // MAX_PAYLOAD_SIZE + 1
        num_segments = (len(data) + MAX_PAYLOAD_SIZE - 1) // MAX_PAYLOAD_SIZE
        for i in range(num_segments):
            start = i * MAX_PAYLOAD_SIZE
            end = min(start + MAX_PAYLOAD_SIZE, len(data))
            payload = data[start:end]
            segment = TransportProtocolSegment(
                self.current_seq_num,
                False,
                False,
                payload,
            )
            segment_bytes = segment.to_bytes()
            self.socket.sendto(segment_bytes, self.dest_address)

            while True:
                ack_received, segment = self.wait_for_ack_or_fin()
                if ack_received and segment.is_fin():
                    self.logger.debug(
                        f"Received FIN for seq number {self.current_seq_num} from {self.dest_address}"
                    )
                    return True
                if ack_received:
                    break
                self.socket.sendto(segment_bytes, self.dest_address)
            self._change_seq_number()
        return False

    def send_server_file_to_client(self, data: bytes):
        # num_segments = len(data) // MAX_PAYLOAD_SIZE + 1
        num_segments = (len(data) + MAX_PAYLOAD_SIZE - 1) // MAX_PAYLOAD_SIZE
        for i in range(num_segments):
            start = i * MAX_PAYLOAD_SIZE
            end = min(start + MAX_PAYLOAD_SIZE, len(data))
            payload = data[start:end]
            segment = TransportProtocolSegment(
                self.current_seq_num,
                False,
                False,
                payload,
            )
            self._enqueue_segment(segment)
            while True:
                ack_received, ack_segment = self.server_wait_ack()
                if ack_received and ack_segment.is_fin():
                    self.logger.debug(
                        f"Received FIN for seq number {self.current_seq_num} from {self.dest_address}"
                    )
                    return True
                if ack_received:
                    break
                self._enqueue_segment(segment)
            self._change_seq_number()
        return False

    def close_connection(self):
        for i in range(NUM_FIN_SEGMENTS_TO_SEND):
            ack_segment = TransportProtocolSegment.create_fin(self.current_seq_num)
            self.socket.sendto(ack_segment.to_bytes(), self.dest_address)
            self.logger.debug(f"FIN sent for seq {self.current_seq_num}")
            time.sleep(RETRANSMIT_TIMER)
