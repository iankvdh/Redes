#!/usr/bin/env python
from mininet.net import Mininet
from mininet.node import OVSController, Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from mininet.term import makeTerms

IP_SERVER = "192.168.1.2/24"
IP_ROUTER = "192.168.1.1/24"
IP_H2 = "192.168.2.2/24"
IP_H3 = "192.168.3.2/24"
IP_H4 = "192.168.3.3/24"


class LinuxRouter(Node):
    """Router con capacidad de forwarding IP"""

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Habilitamos el forwarding IP
        self.cmd("sysctl net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl net.ipv4.ip_forward=0")
        super(LinuxRouter, self).terminate()


def lossTopology():
    net = Mininet(controller=OVSController, link=TCLink)

    info("*** Agregando Controlador\n")
    net.addController("c0")

    info("*** Agregando Hosts\n")
    server = net.addHost("server", ip=IP_SERVER, defaultRoute="via 192.168.1.1")
    h2 = net.addHost("h2", ip=IP_H2, defaultRoute="via 192.168.2.1")
    h3 = net.addHost("h3", ip=IP_H3, defaultRoute="via 192.168.3.1")
    h4 = net.addHost(
        "h4", ip=IP_H4, defaultRoute="via 192.168.3.1"
    )  # REVISAR (conecta un nuevo cliente desde la misma red que el anterior)

    info("*** Agregando Switches\n")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")
    s3 = net.addSwitch("s3")

    info("*** Agregando Router\n")
    router = net.addHost("r1", cls=LinuxRouter, ip=IP_ROUTER)

    info("*** Creando Links\n")
    # Enlace normal entre server y s1 con perdida de paquetes al 10%
    net.addLink(server, s1, loss=10)

    net.addLink(s1, router, intfName2="r1-etserver", params2={"ip": "192.168.1.1/24"})

    net.addLink(router, s2, intfName1="r1-eth2", params1={"ip": "192.168.2.1/24"})
    net.addLink(router, s3, intfName1="r1-eth3", params1={"ip": "192.168.3.1/24"})

    net.addLink(s2, h2)
    net.addLink(s3, h3)
    net.addLink(s3, h4)

    for host in (server, h2, h3, h4):
        host.cmd("sysctl -w net.ipv4.ip_no_pmtu_disc=1")

    info("*** Comenzando Red\n")
    net.start()

    info("*** Comenzando terminales para server y h2 con xterm\n")
    makeTerms([server, h2, h3, h4], term="xterm")

    info("*** Comenzando CLI\n")
    CLI(net)

    info("*** Frenando la Red al hacer exit\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    lossTopology()
