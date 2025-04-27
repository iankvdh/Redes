from queue import *
from socket import *
from threading import Thread
from .user_manager import *
from .transport_protocols.protocol_segment import TransportProtocolSegment
import traceback

# data, addr = sock.recvfrom(4096)  # addr es una tupla: (ip, puerto)
MAX_SEGMENT_SIZE = 4096


class ServerReceiver:
    def __init__(self, socket, protocol_type, storage_path):
        self.__socket = socket
        self.__protocol_type = protocol_type
        self.__storage_path = storage_path
        self.__clients: dict[tuple[str, int], Thread] = (
            {}
        )  # asocia tupla ip, port con cada hilo
        self.__queues: dict[tuple[str, int], Queue] = {}

    def run(self):
        # Recibir un segmento de la red
        # Me fijo a qué cliente le corresponde
        # Lo encolo en la cola que corresponda
        # Repetir
        print("ServerReceiver iniciado")
        while True:
            try:
                m_bytes, client_address = self.__socket.recvfrom(MAX_SEGMENT_SIZE)
                segment = TransportProtocolSegment.from_bytes(m_bytes)

                # si llega un segmento con el flag FIN hacer brake
                if segment.fin:
                    break

                # Si el cliente no existe, lo creo y lo inicio
                if client_address not in self.__clients:
                    print(f"Nuevo cliente conectado: {client_address}")
                    new_client_queue = Queue()
                    new_user_manager = UserManager(
                        self.__socket,
                        new_client_queue,
                        client_address,
                        self.__protocol_type,
                        self.__storage_path,
                    )

                    new_client_thread = Thread(target=new_user_manager.run)
                    new_client_thread.start()

                    new_client_queue.put(segment)

                    self.__queues[client_address] = new_client_queue
                    self.__clients[client_address] = new_client_thread

                else:
                    self.__queues[client_address].put(segment)
            except OSError as e:
                break
            except Exception as e:
                print(f"Error en el ServerReceiver: {e}")
                traceback.print_exception(type(e), e, e.__traceback__)
                break

        print("ServerReceiver cerrado")

    def close(self):
        for client in self.__clients.values():
            client.join()
