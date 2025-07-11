import os
import socket as skt
from lib.transport_protocols.stop_and_wait import StopAndWait
from lib.transport_protocols.selective_repeat import SelectiveRepeat
import traceback
from lib.constants import (
    CHUNK_SIZE,
    STOP_AND_WAIT,
    SELECTIVE_REPEAT,
)


class Client:
    def __init__(self, host, port, protocol_type: str = STOP_AND_WAIT, logger=None):
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        # AF_INET significa usar IPv4
        # SOCK_DGRAM significa usar UDP
        self.logger = logger
        if protocol_type == STOP_AND_WAIT:
            self.__protocol = StopAndWait.create_client_stop_and_wait(
                self.socket, (host, port), self.logger
            )
        elif protocol_type == SELECTIVE_REPEAT:
            self.__protocol = SelectiveRepeat.create_client_selective_repeat(
                self.socket, (host, port), self.logger
            )
        self.logger.info(f"Client initialized with protocol {protocol_type}.")

    def upload_file(self, source_file_path: str, file_name: str):
        """
        Upload a file to the server.
        """
        try:
            self.logger.info(f"Uploading file {file_name} to the server.")
            file_size = os.path.getsize(source_file_path)
            self.__protocol.start_upload(file_name, file_size)
            with open(source_file_path, "rb") as file:
                while True:
                    chunk = file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    closed_connection = self.__protocol.send_client_file_to_server(
                        chunk
                    )
                    if closed_connection:
                        break
            self.logger.info(f"File {source_file_path} uploaded successfully.")

        except FileNotFoundError:
            if source_file_path == "":
                self.logger.error(
                    "File path is empty. Provide a valid file path with: python upload.py -s <file_path>"
                )
            else:
                self.logger.error(f"File not found: {source_file_path}")
        except Exception as e:
            self.logger.error(f"An error occurred while uploading the file: {e}")
        finally:
            self.close()

    def download_file(self, dest_file_path: str, file_name: str):
        """
        Download a file from the server.
        """
        try:
            file_exists, file_size = self.__protocol.start_download(file_name)
            if not file_exists:
                raise FileNotFoundError()
            with open(f"{dest_file_path}/{file_name}", "wb") as file:
                remaining_data_size = file_size
                self.logger.debug(
                    f"Downloading file {file_name} of size {file_size} bytes."
                )
                while remaining_data_size > 0:
                    chunk = self.__protocol.receive_file_from_server(
                        min(CHUNK_SIZE, remaining_data_size)
                    )
                    if len(chunk) == 0:
                        break
                    file.write(chunk)
                    remaining_data_size -= len(chunk)
            self.logger.info(f"File {file_name} downloaded successfully.")
        except FileNotFoundError:
            self.logger.error(f"The file '{file_name}' does not exist on the server.")
        except Exception as e:
            self.logger.error(f"An error occurred while downloading the file: {e}")
            traceback.print_exception(type(e), e, e.__traceback__)
        finally:
            self.__protocol.close_connection()
            self.close()

    def close(self):
        """
        Close the connection.
        """
        self.__protocol.stop()
        self.socket.close()
        self.logger.info("Client closed.")
