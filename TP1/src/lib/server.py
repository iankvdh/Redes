from socket import *
from queue import *
from threading import *
from lib.server_receiver import *
from lib.server_sender import *

class Server:
    def __init__(self, host, port, protocol_type: str, storage_path: str = ""):
        self.__host = host
        self.__port = port
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.protocol_type = protocol_type
        self.__storage_path = storage_path
        """
        if protocol_type == "sw":
            self.__protocol = tp.StopAndWait.create()
        elif protocol_type == "sr":
            self.__protocol == tp.SelectiveRepeat.create()
        """
        self.__server_receiver = ServerReceiver(self.socket, self.protocol_type, self.__storage_path)
        #self.__server_sender = ServerSender(self.socket, self.protocol_type, self.__storage_path)

    def start(self):
        try: 
            self.socket.bind((self.__host, self.__port))
            print("Iniciamos el server!")

        except socket.error as e:
            print(f"Exploto el socket: {e}")
            return

        thread_receiver = Thread(target=self.__server_receiver.run)
        #thread_sender = Thread(target=self.__server_sender.run, args=(...))
        thread_receiver.start()
        #thread_sender.start()
        # si me llega un exit por input (consola), se cierra el server
        while input() != "exit":
            pass

        self.__server_receiver.close()
        thread_receiver.join()
        #thread_sender.join()
        self.socket.close()
        print("Server cerrado")

            

        
        
