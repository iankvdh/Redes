WINDOWS_SIZE = 4

class StopAndWait:
    def __init__(self, socket, address, msg_queue):
        self.timeout = 1000 # Unidad: Milisegundos
        self.socket = socket
        self.address = address
        self.msg_queue = msg_queue
        self.window_size = WINDOWS_SIZE

    @classmethod
    def create_client_selective_repeat(cls, socket, address):
        return cls(socket, address, None)
    
    @classmethod
    def create_server_selective_repeat(cls, socket, address, msg_queue):
        return cls(socket, address, msg_queue)
    
    def send_ack(self):
        pass

    def wait_ack(self):
        pass

    def send_client_file(self):
        pass

    def receive_client_file(self):
        pass

    def send_server_file(self):
        pass

    def receive_server_file(self):
        pass
