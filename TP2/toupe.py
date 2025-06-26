#!/usr/bin/env python
from mininet.topo import Topo


class Toupe(Topo):
    def __init__(self, switches=3):
        Topo.__init__(self)

        # Hosts
        h1 = self.addHost("h1", mac="00:00:00:00:01:01", ip="10.0.0.1")
        h2 = self.addHost("h2", mac="00:00:00:00:01:02", ip="10.0.0.2")
        h3 = self.addHost("h3", mac="00:00:00:00:01:03", ip="10.0.0.3")
        h4 = self.addHost("h4", mac="00:00:00:00:01:04", ip="10.0.0.4")

        # Switches
        switches_list = [self.addSwitch(f"s{i + 1}") for i in range(switches)]

        # Links entre hosts y switches
        self.addLink(h1, switches_list[0])
        self.addLink(h2, switches_list[0])
        self.addLink(h3, switches_list[-1])
        self.addLink(h4, switches_list[-1])

        # Links entre switches
        for i in range(switches - 1):
            self.addLink(switches_list[i], switches_list[i + 1])


topos = {"toupe": Toupe}


"""

s1 ---- s2

   --->

"""
