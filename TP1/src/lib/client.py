import os
import socket as skt
from lib.transport_protocols.stop_and_wait import StopAndWait
from lib.transport_protocols.selective_repeat import SelectiveRepeat

_CHUNK_SIZE = 4096


class Client:
    def __init__(self, host, port, protocol_type: str = "sw"):
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        # AF_INET significa usar IPv4
        # SOCK_DGRAM significa usar UDP

        # client_sender = ClientSender(self.socket)
        # client_receiver = ClientReceiver(self.socket)

        if protocol_type == "sw":
            self.__protocol = StopAndWait.create_client_stop_and_wait(
                self.socket, (host, port)
            )
        elif protocol_type == "sr":
            self.__protocol == SelectiveRepeat.create_client_selective_repeat(
                self.socket, (host, port)
            )

    def upload_file(self, source_file_path: str, file_name: str):
        """
        Upload a file to the server.
        """

        # [ ........ ] -> archivo entero
        # [..] [..] [..] [..] -> chunks del archivo
        # ----
        # [.] [.] -> Enviar
        # [.] [.] -> Enviar
        # [.] [.] -> Enviar
        # [.] [.] -> Enviar
        try:
            file_size = os.path.getsize(source_file_path)
            # Send the file name first
            self.__protocol.start_upload(file_name, file_size)
            with open(source_file_path, "rb") as file:
                while True:
                    chunk = file.read(_CHUNK_SIZE)
                    if not chunk:
                        break
                    self.__protocol.send(chunk)
            self.close()

        except FileNotFoundError:
            if source_file_path == "":
                print(
                    "File path is empty. Please, provide a valid file path with -> python upload.py -s <file_path>"
                )
            else:
                print(f"File {source_file_path} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def download_file(self, dest_file_path: str, file_name: str):
        """
        Download a file from the server.
        """
        self.__protocol.start_download(file_name)
        with open(dest_file_path, "wb") as file:
            while True:
                chunk = self.__protocol.receive(_CHUNK_SIZE)
                if not chunk:
                    break
                file.write(chunk)
        self.close()

    def close(self):
        """
        Close the connection.
        """
        self.socket.close()
        print("Connection closed.")
