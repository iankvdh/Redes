_CHUNK_SIZE = 4096  # 4 KB por ejemplo


class Client:
    def __init__(self, protocol):

        self.__protocol = protocol

    def upload_file(self, file_path: str):
        """
        Upload a file to the server.
        """
        self.__protocol.start_upload()
        # Three Way Handshake: SYN, SYN ACK, ACK. Envia tamaño de la ventana tambien.
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(_CHUNK_SIZE)
                if not chunk:
                    break
                self.__protocol.send(chunk)

        self.__protocol.end_upload()

    def download_file(self, file_path: str):
        """
        Download a file from the server.
        """
        self.__protocol.start_download()
        with open(file_path, "wb") as file:
            while True:
                chunk = self.__protocol.receive()
                if not chunk:
                    break
                file.write(chunk)
        self.__protocol.end_download()
