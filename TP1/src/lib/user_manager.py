from queue import *
from socket import *
from threading import *
from lib.transport_protocols.stop_and_wait import StopAndWait
from lib.transport_protocols.selective_repeat import SelectiveRepeat
import traceback

_CHUNK_SIZE = 4096


class UserManager:
    def __init__(
        self, socket, queue, client_address, protocol_type, storage_path, is_upload=True
    ):
        self.__socket = socket
        self.__client_address = client_address
        if protocol_type == "sw":
            self.__protocol = StopAndWait.create_server_stop_and_wait(
                self.__socket, self.__client_address, queue
            )
        elif protocol_type == "sr":
            self.__protocol = SelectiveRepeat.create_server_selective_repeat(
                self.__socket, self.__client_address, queue
            )
        self.__storage_path = storage_path
        self.__is_upload = True

    def run(self):
        try:
            while True:
                if self.__is_upload:
                    file_size, file_name, is_upload = (
                        self.__protocol.receive_file_info()
                    )
                    print(f"Recibiendo archivo {file_name} de {file_size} bytes")
                    with open(f".{self.__storage_path}/{file_name}", "wb") as file:
                        remaining_data_size = file_size
                        while remaining_data_size > 0:
                            chunk = self.__protocol.receive(
                                _CHUNK_SIZE
                            )  # chunk es un bytearray
                            if len(chunk) == 0:
                                break
                            file.write(chunk)
                            remaining_data_size -= len(chunk)

                else:
                    # serializar archivos
                    # toma archivos de la carpeta y parte en chunks
                    # luego los manda al cliente
                    self.__protocol.send_server_file()

        except Exception as e:
            print(f"Error en el UserManager: {e}")
            traceback.print_tb(e.__traceback__)
            print(f"Error: {e}")
