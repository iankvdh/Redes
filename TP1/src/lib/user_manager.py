from queue import *
from socket import *
from threading import *
from lib.transport_protocols.stop_and_wait import StopAndWait
from lib.transport_protocols.selective_repeat import SelectiveRepeat

class UserManager:
    def __init__(self, socket, queue, client_address, protocol_type, storage_path, is_upload=True):
        self.__socket = socket
        self.__client_address = client_address
        if protocol_type == "sw":
            self.__protocol = StopAndWait.create_server_stop_and_wait(self.__socket, self.__client_address, queue)
        elif protocol_type == "sr":
            self.__protocol = SelectiveRepeat.create_server_selective_repeat(self.__socket, self.__client_address, queue)
        self.__storage_path = storage_path
        self.__is_upload = True
        
    def run(self):
        try:
            while True:
                if self.__is_upload:
                    file_name, file_size = self.__protocol.receive_file_info()
                    print(f"Recibiendo archivo {file_name} de {file_size} bytes")
                    with open(f"{self.__storage_path}/{file_name}", "wb") as file:
                        while file_size > 0:
                            chunk = self.__protocol.receive_server_file()
                            if chunk is None:
                                break
                            file.write(chunk)
                            file_size -= len(chunk)
                        

                else:
                    # serializar archivos
                    # toma archivos de la carpeta y parte en chunks
                    # luego los manda al cliente
                    self.__protocol.send_server_file()

        except Exception as e:
            print(f"Error en el UserManager: {e}")
