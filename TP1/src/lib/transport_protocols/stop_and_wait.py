
class StopAndWait:
    def __init__(self, capa_inf_recv, capa_inf_trans):
        self.timeout = 1000 # Unidad: Milisegundos

    def create(self):
        return self
