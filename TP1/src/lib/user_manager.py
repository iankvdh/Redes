from queue import *
from socket import *
from threading import *
from lib.transport_protocols.stop_and_wait import StopAndWait
from lib.transport_protocols.selective_repeat import SelectiveRepeat
import traceback
import os

_CHUNK_SIZE = 4096
_STOP_AND_WAIT = "sw"
_SELECTIVE_REPEAT = "sr"

class UserManager:
    def __init__(
        self, socket, client_queue, send_queue ,client_address, protocol_type, storage_path, logger=None 
    ):
        self.__socket = socket
        self.__client_address = client_address
        self.logger = logger
        if protocol_type == _STOP_AND_WAIT:
            self.__protocol = StopAndWait.create_server_stop_and_wait(
                self.__socket, self.__client_address, client_queue, send_queue, logger
            )
        elif protocol_type == _SELECTIVE_REPEAT:
            self.__protocol = SelectiveRepeat.create_server_selective_repeat(
                self.__socket, self.__client_address, client_queue, logger
            )
        self.__storage_path = storage_path
        self.is_alive = True

    def run(self):
        try:
            file_size, file_name, is_upload = self.__protocol.receive_file_info_to_start()
            if is_upload:
                with open(f"{self.__storage_path}/{file_name}", "wb") as file:
                    remaining_data_size = file_size
                    while remaining_data_size > 0:
                        chunk = self.__protocol.receive_file_from_client(
                            min(_CHUNK_SIZE, remaining_data_size)
                        )  # chunk es un bytearray
                        if len(chunk) == 0:
                            break
                        file.write(chunk)
                        remaining_data_size -= len(chunk)
            else:
                file_path = os.path.join(self.__storage_path, file_name)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)  # Obtiene el tamaño en bytes
                    self.__protocol.send_file_size_to_client(file_size)
                    with open(file_path, "rb") as file:
                        while True:
                            chunk = file.read(_CHUNK_SIZE)
                            if not chunk:
                                break
                            self.__protocol.send_server_file_to_client(chunk)
                    self.logger.info(f"File {file_path} downloaded successfully.")
                else:
                    self.logger.debug(f"File {file_path} does not exist on server.")
                    self.__protocol.send_file_does_not_exist()

        except Exception as e:
            traceback.print_tb(e.__traceback__)
        finally:
            self.close()

    def close(self):
        self.is_alive = False
