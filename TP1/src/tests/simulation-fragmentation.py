#!/usr/bin/env python
from mininet.net import Mininet
from mininet.node import OVSController, Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

MIN_MTU = 500
MAX_MTU = 1500

IP_SERVER = "192.168.1.2/24"
IP_ROUTER = "192.168.1.1/24"
IP_H2 = "192.168.2.2/24"


class LinuxRouter(Node):
    """Router con capacidad de forwarding IP y MTU reducido"""

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Habilitamos el forwarding IP
        self.cmd("sysctl net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl net.ipv4.ip_forward=0")
        super(LinuxRouter, self).terminate()


def fragTopology():
    net = Mininet(controller=OVSController, link=TCLink)

    info("*** Agregando Controlador\n")
    net.addController("c0")

    info("*** Agregando Hosts\n")
    server = net.addHost("server", ip=IP_SERVER, defaultRoute="via 192.168.1.1")
    h2 = net.addHost("h2", ip=IP_H2, defaultRoute="via 192.168.2.1")

    info("*** Agregando Switches\n")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")

    info("*** Agregando Router\n")
    router = net.addHost("r1", cls=LinuxRouter, ip=IP_ROUTER)

    info("*** Creando Links\n")

    net.addLink(server, s1, cls=TCLink, mtu=MAX_MTU)

    net.addLink(
        s1,
        router,
        intfName2="r1-etserver",
        params2={"ip": IP_ROUTER},
        cls=TCLink,
        mtu=MIN_MTU,
    )

    net.addLink(
        router,
        s2,
        intfName1="r1-eth2",
        params1={"ip": "192.168.2.1/24"},
        cls=TCLink,
        mtu=MAX_MTU,
    )

    net.addLink(s2, h2, cls=TCLink, mtu=MAX_MTU, loss=10)  # Pérdida del 10%

    for host in (server, h2):
        host.cmd(
            "sysctl -w net.ipv4.ip_no_pmtu_disc=1"
        )  # desactivar la detección de MTU en extremos

    info("*** Comenzando Red\n")
    net.start()

    # Configurar MTU en las interfaces del router
    router.cmd(f"ifconfig r1-eth2 mtu {MIN_MTU}")

    info("*** Comenzando CLI\n")
    CLI(net)

    info("*** Frenando la Red al hacer exit\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    fragTopology()
