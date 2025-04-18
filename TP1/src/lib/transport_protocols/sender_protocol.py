from abc import ABC, abstractmethod

class SenderProtocol(ABC): #Envía datos desde la capa superior a la inferior
    def __init__(self, capa_inferior):
        self.capa_inferior = capa_inferior
        pass

    # protocolo.send_data("linea del archivo") 
    def send_data(self, data):
        # Procesar data / separar en segmentos / etc
        # capa_inferior.send_data(data)
        pass

    def run(self):
        while True:
            # Recibe datos de la capa superior
            data = self.capa_superior.get_data()
            # Procesa los datos
            processed_data = self.process_data(data)
            # Envía los datos a la capa inferior
            self.capa_inferior.send_data(processed_data)


    
# t1 = TransportProtocol(...)

# thread1 = threading.Thread(target=t1.run)
# thread1.start()