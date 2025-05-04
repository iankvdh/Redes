from socket import *
from queue import *
from threading import *
from lib.server_receiver import *
from lib.server_sender import *
from lib.transport_protocols.protocol_segment import TransportProtocolSegment


class Server:
    def __init__(self, host, port, protocol_type: str, storage_path: str, logger=None):
        self.__host = host
        self.__port = port
        self.socket = socket.socket(AF_INET, SOCK_DGRAM)
        self.protocol_type = protocol_type
        self.__storage_path = storage_path
        self.logger = logger
        self.__send_queue = Queue()

        self.__server_sender = ServerSender(
            self.socket, self.__send_queue, self.logger
        )
        self.__server_receiver = ServerReceiver(
            self.socket,
            self.protocol_type,
            self.__storage_path,
            self.__send_queue,
            self.logger,
        )
        self.__thread_sender = Thread(target=self.__server_sender.run)
        self.__thread_receiver = Thread(target=self.__server_receiver.run)

    def start(self):
        try:
            self.socket.bind((self.__host, self.__port))
            self.logger.info(f"Server inicialized on {self.__host}:{self.__port}")

        except socket.timeout as e:
            self.logger.error(f"Socket timeout error in server: {e}")
            return
        
        self.__thread_receiver.start()
        self.__thread_sender.start()
        # si me llega un exit por input (consola), se cierra el server
        while input() != "exit":
            pass

        # Cuando llega un exit a la consola del servidor, se crea un fin_segment
        # que es enviado al socket para despertar al recvfrom de ServerReceiver
        # y avisarle que tiene que salir del while
        fin_segment = TransportProtocolSegment.create_fin(0, 0)
        self.socket.sendto(fin_segment.to_bytes(), (self.__host, self.__port))

        self.__server_receiver.close()

        self.__thread_receiver.join()

        self.__server_sender.close()
        self.__thread_sender.join()
        
        self.socket.close()

        self.logger.info("Server closed.")
