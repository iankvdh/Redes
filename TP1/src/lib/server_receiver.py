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
        self.__clients: dict[tuple[str, int], UserManager] = {}
        self.__client_threads: dict[tuple[str, int], Thread] = {}
        self.__queues: dict[tuple[str, int], Queue] = {}
        self.__send_queue = send_queue
        self.logger = logger

    def run(self):
        while True:
            try:
                segment, client_address = self._receive_segment()
                if client_address == self.__socket.getsockname():
                    self.logger.debug("Received FIN segment, stopping receiver thread")
                    break
                self._dispatch_segment(client_address, segment)
            except OSError as e:
                """ 
                if # SI HUBO UN TIMEOUT, HAY QUE CERRAR ALGUN CLIENTE QUE NO RESPONDE:
                    self.logger.info(f"Cliente desconectado: {client_address}")
                    if client_address in self.__clients:
                        del self.__clients[client_address]
                        del self.__queues[client_address]
                else:
                    self.logger.error(f"Error on the socket: {e}")
                """
                traceback.print_exception(type(e), e, e.__traceback__)
            except Exception as e:
                self.logger.error(f"Error in ServerReceiver: {e}")
                traceback.print_exception(type(e), e, e.__traceback__)
                break
        self.logger.debug("Closed Server Receiver thread")

    def _receive_segment(self):
        m_bytes, client_address = self.__socket.recvfrom(MAX_SEGMENT_SIZE)
        segment = TransportProtocolSegment.from_bytes(m_bytes)
        self.logger.debug(f"Received segment with sequence number {segment.seq_num} from {client_address}")
        return segment, client_address

    def _dispatch_segment(self, client_address, segment):
        if client_address not in self.__client_threads:
            self.logger.info(f"New client connected: {client_address}")
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
        self.__clients[client_address] = user_manager
        self.__client_threads[client_address] = thread

    def close(self):
        for address in self.__client_threads:
            self.__clients[address].close()            
            self.__client_threads[address].join()
        self.logger.debug("Closing all client handlers.")
