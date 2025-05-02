from queue import *
from socket import *
from threading import Thread
from .user_manager import *
from .transport_protocols.protocol_segment import TransportProtocolSegment
import traceback

# data, addr = sock.recvfrom(4096)  # addr es una tupla: (ip, puerto)
MAX_SEGMENT_SIZE = 4096

class ServerReceiver:
    def __init__(self, socket, protocol_type, storage_path, send_queue,logger=None):
        self.__socket = socket
        self.__protocol_type = protocol_type
        self.__storage_path = storage_path
        self.__clients: dict[tuple[str, int], Thread] = {}
        self.__queues: dict[tuple[str, int], Queue] = {}
        self.__send_queue = send_queue
        self.logger = logger

    def run(self):
        self.logger.info("Iniciando ServerReceiver")
        while True:
            try:
                segment, client_address = self._receive_segment()
                if client_address == self.__socket.getsockname():
                    self.logger.info("Cerrando ServerReceiver")
                    break
                self._dispatch_segment(client_address, segment)

            except OSError as e:
                traceback.print_exception(type(e), e, e.__traceback__)

            except Exception as e:
                self.logger.error(f"Error en el ServerReceiver: {e}")
                traceback.print_exception(type(e), e, e.__traceback__)
                break

        self.logger.info("Cerrado ServerReceiver")

    def _receive_segment(self):
        m_bytes, client_address = self.__socket.recvfrom(MAX_SEGMENT_SIZE)
        segment = TransportProtocolSegment.from_bytes(m_bytes)
        self.logger.debug(f"Recibido segmento de {client_address}: {segment}")
        return segment, client_address

    def _dispatch_segment(self, client_address, segment):
        if client_address not in self.__clients:
            self.logger.info(f"Nuevo cliente conectado: {client_address}")
            self._create_client_handler(client_address, segment)
        else:
            self.__queues[client_address].put(segment)

    def _create_client_handler(self, client_address, initial_segment):
        client_queue = Queue()
        user_manager = UserManager(
            self.__socket,
            client_queue,
            self.__send_queue,
            client_address,
            self.__protocol_type,
            self.__storage_path,
            self.logger
        )
        thread = Thread(target=user_manager.run)
        thread.start()

        client_queue.put(initial_segment)

        self.__queues[client_address] = client_queue
        self.__clients[client_address] = thread

    def close(self):
        for client in self.__clients.values():
            client.join()
        self.logger.info("Cerrados todos los hilos de los clientes")
