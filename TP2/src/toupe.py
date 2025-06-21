#!/usr/bin/env python
from mininet.topo import Topo


class Toupe(Topo):
    def __init__(self, switches=3):
        Topo.__init__(self)

        # Agregar hosts
        h1 = self.addHost("h1", mac="00:00:00:00:01:01")
        h2 = self.addHost("h2", mac="00:00:00:00:01:02")
        h3 = self.addHost("h3", mac="00:00:00:00:01:03")
        h4 = self.addHost("h4", mac="00:00:00:00:01:04")


        # Agregar switches
        switches_list = [self.addSwitch(f"s{i + 1}") for i in range(switches)]
        
        # Conectar hosts a switches
        self.addLink(h1, switches_list[0])
        self.addLink(h2, switches_list[0])
        self.addLink(h3, switches_list[-1])
        self.addLink(h4, switches_list[-1])

        # Conectar switches entre sí
        for i in range(switches - 1):
            self.addLink(switches_list[i], switches_list[i + 1])

topos = {'toupe': Toupe}


"""

s1 ---- s2

   --->

"""