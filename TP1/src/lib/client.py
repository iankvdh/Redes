from socket import *
import transport_protocols as tp
import os

_CHUNK_SIZE = 1024  # 1 KB por ejemplo


class Client:
    def __init__(self, host, port, protocol_type: str = "sw"):
        self.socket = socket(socket.AF_INET, socket.SOCK_DGRAM)
        # AF_INET significa usar IPv4
        # SOCK_DGRAM significa usar UDP
        
        # client_sender = ClientSender(self.socket)
        # client_receiver = ClientReceiver(self.socket)
        
        if protocol_type == "sw":
            self.__protocol = tp.StopAndWait.create()
        elif protocol_type == "sr":
            self.__protocol == tp.SelectiveRepeat.create()
            
        self.socket = socket.connect((host, port))

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
        
        file_size = os.path.getsize(source_file_path)
        # Send the file name first
        self.__protocol.start_upload(file_name, file_size)
        with open(source_file_path, "rb") as file:
            while True:
                chunk = file.read(_CHUNK_SIZE)
                if not chunk:
                    break
                self.__protocol.send_data(chunk)
        self.close()


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
        self.__protocol.close()
        self.socket.close()