from .protocol_segment import *

_START_SECUENCE_NUMBER = 0
_START_ACK_NUMBER = 0

class StopAndWait:
    def __init__(self, socket, dest_address, msg_queue):
        self.timeout = 1000 # Unidad: Milisegundos
        self.socket = socket
        self.dest_address = dest_address
        self.msg_queue = msg_queue

    @classmethod
    def create_client_stop_and_wait(cls, socket, address):
        return cls(socket, address, None)
    
    @classmethod
    def create_server_stop_and_wait(cls, socket, address, msg_queue):
        return cls(socket, address, msg_queue)
    
    def start_upload(self, file_name, file_size):
        print(f"Starting upload with {file_name} and size {file_size} bytes")
        # convertir file_size en bytes big-endian
        file_size_bytes = file_size.to_bytes(4, byteorder='big')
        # enviar nombre de archivo y tamaño
        payload = file_name.encode() + b'\0' + file_size_bytes # ¿POR QUÉ EL CERO?
        # creo segmento de transporte
        segment = TransportProtocolSegment(_START_SECUENCE_NUMBER, _START_ACK_NUMBER, False, False, False, True, payload)
        # lo convierto a bytes
        data = segment.to_bytes()
        # lo envio
        self.socket.sendto(data, self.dest_address)
        print(f"Sent upload request to {self.dest_address}")
        
    def start_download(self, file_name):
        pass

    def send_ack(self):
        pass

    def wait_ack(self):
        pass

    def send_client_file(self):
        pass

    def receive_client_file(self):
        pass

    def send_server_file(self):
        pass

    def receive_server_file(self):
        # extraigo segmentos de la queue
        m_bytes = self.msg_queue.get()
        return m_bytes

    def receive_file_info(self):
        # Recibo el nombre del archivo y su tamaño
        m_bytes = self.msg_queue.get()
        segment = TransportProtocolSegment.from_bytes(m_bytes)
        file_name, file_size = segment.payload.split(b'\0')
        file_size = int.from_bytes(file_size, byteorder='big')
        return file_name.decode(), file_size
