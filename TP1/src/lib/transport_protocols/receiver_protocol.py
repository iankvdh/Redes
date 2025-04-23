from abc import ABC, abstractmethod

class ReceiverProtocol(ABC): #Recibe datos desde 
    


    @abstractmethod
    def receive_data(self, size: int):
        # Procesar data / separar en segmentos / etc
        # capa_inferior.send_data(data)
        pass


    