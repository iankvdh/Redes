
class ServerSender:
    def __init__(self, socket, protocol_type):
        self.__socket = socket
        self.__protocol_type = protocol_type