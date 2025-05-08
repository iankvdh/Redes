from lib.transport_protocols.stop_and_wait import StopAndWait
from lib.transport_protocols.selective_repeat import SelectiveRepeat
import traceback
import os
from lib.constants import (
    CHUNK_SIZE,
    STOP_AND_WAIT,
    SELECTIVE_REPEAT,
)


class UserManager:
    def __init__(
        self,
        socket,
        client_queue,
        send_queue,
        client_address,
        protocol_type,
        storage_path,
        logger=None,
    ):
        self.__socket = socket
        self.__client_address = client_address
        self.logger = logger
        if protocol_type == STOP_AND_WAIT:
            self.__protocol = StopAndWait.create_server_stop_and_wait(
                self.__socket, self.__client_address, client_queue, send_queue, logger
            )
        elif protocol_type == SELECTIVE_REPEAT:
            self.__protocol = SelectiveRepeat.create_server_selective_repeat(
                self.__socket, self.__client_address, client_queue, send_queue, logger
            )
        self.__storage_path = storage_path

    def run(self):
        try:
            file_size, file_name, is_upload = (
                self.__protocol.receive_file_info_to_start()
            )
            if is_upload:
                self.logger.info(
                    f"Uploading file {file_name} from {self.__client_address}."
                )
                with open(f"{self.__storage_path}/{file_name}", "wb") as file:
                    remaining_data_size = file_size
                    while remaining_data_size > 0:
                        chunk = self.__protocol.receive_file_from_client(
                            min(CHUNK_SIZE, remaining_data_size)
                        )  # chunk es un bytearray
                        if len(chunk) == 0:
                            break
                        file.write(chunk)
                        remaining_data_size -= len(chunk)
                self.logger.info(f"File {file_name} uploaded successfully.")
                self.__protocol.close_connection()
            else:
                file_path = os.path.join(self.__storage_path, file_name)
                if os.path.isfile(file_path):
                    self.logger.info(
                        f"Downloading file {file_name} to {self.__client_address}."
                    )
                    file_size = os.path.getsize(file_path)
                    self.__protocol.send_file_size_to_client(file_size)
                    with open(file_path, "rb") as file:
                        while True:
                            chunk = file.read(CHUNK_SIZE)
                            if not chunk:
                                break
                            closed_connection = (
                                self.__protocol.send_server_file_to_client(chunk)
                            )
                            if closed_connection:
                                break
                    self.logger.info(f"File {file_path} downloaded successfully.")
                else:
                    self.logger.error(f"File {file_path} does not exist on server.")
                    self.__protocol.send_file_does_not_exist()

        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
        finally:
            self.close()

    def close(self):
        self.__protocol.stop()
