from queue import *
from socket import *
from threading import Thread


# data, addr = sock.recvfrom(4096)  # addr es una tupla: (ip, puerto)

class ServerReceiver:
    def __init__(self, socket, protocol_type):
        self.__socket = socket
        self.__protocol_type = protocol_type
        self.__clients: dict[tuple[str, int], Thread] = {} # asocia tupla ip, port con cada hilo
        self.__queues: dict[tuple[str, int], Queue] = {}

    def run(self):
        # Recibir un segmento de la red
        # Me fijo a qué cliente le corresponde
        # Lo encolo en la cola que corresponda
        # Repetir
        
        while True:
            try:
                m_bytes, client_address = self.__socket.recvfrom()
                
                if client_address not in self.__clients:
                    new_client_queue = Queue()
                    new_client_thread = Thread(target=UserManager().run, args=(...))
 
                    new_client_queue.put(m_bytes)
                    self.__queues[client_address] = new_client_queue
                    self.__clients[client_address] = new_client_thread

                else: 
                    self.__queues[client_address].put(m_bytes)
                    
            except Exception as e:
                print(f"Exploto algo al recibir: {e}")

    def close():
        pass