from socket import *
from queue import *
from threading import *
from lib.server_receiver import *
from lib.server_sender import *

class Server:
    def __init__(self, host, port, protocol_type: str):
        self.__host = host
        self.__port = port
        self.socket = socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.protocol_type = protocol_type
        """
        if protocol_type == "sw":
            self.__protocol = tp.StopAndWait.create()
        elif protocol_type == "sr":
            self.__protocol == tp.SelectiveRepeat.create()
        """
        self.__server_receiver = ServerReceiver(self.socket, self.protocol_type)
        self.__server_sender = ServerSender(self.socket, self.protocol_type)

    def start(self):
        try: 
            self.socket.bind((self.__host, self.__port))
            print("Iniciamos el server!")

        except socket.error as e:
            print(f"Exploto el socket: {e}")
            return

        thread_receiver = Thread(target=self.__server_receiver.run, args=(...))
        thread_sender = Thread(target=self.__server_sender.run, args=(...))

        # si me llega un exit por input (consola), se cierra el server
        while input() != "exit":
            pass

        thread_receiver.join()
        thread_sender.join()
        self.__running = False
        self.socket.close()
        print("Server cerrado")

            

        
        
