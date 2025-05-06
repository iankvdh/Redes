#!/usr/bin/env python
from mininet.net import Mininet
from mininet.node import OVSController, Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from mininet.term import makeTerms


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
    h1 = net.addHost("h1", ip="192.168.0.2/30", defaultRoute="via 192.168.0.1")
    h2 = net.addHost("h2", ip="192.168.0.6/30", defaultRoute="via 192.168.0.5")

    info("*** Agregando Switches\n")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")

    info("*** Agregando Router\n")
    router = net.addHost("r1", cls=LinuxRouter, ip="192.168.0.1/30")

    info("*** Creando Links\n")
    net.addLink(h1, s1, intfName1="h1-eth1", intfName2="s1-eth1", mtu=1500)

    net.addLink(
        s1,
        router,
        intfName1="s1-eth2",
        intfName2="r1-eth1",
        params2={"ip": "192.168.0.1/30"},
        mtu=1500,
    )

    net.addLink(
        router,
        s2,
        intfName1="r1-eth2",
        intfName2="s2-eth1",
        params1={"ip": "192.168.0.5/30"},
        cls=TCLink,
        mtu=500,
    )

    # Enlace normal entre s2 y h2 con perdida de paquetes al 10%
    net.addLink(s2, h2, intfName1="s2-eth2", intfName2="h2-eth1", loss=10, mtu=1500)

    h1.cmd("sysctl -w net.ipv4.ip_no_pmtu_disc=1")
    h2.cmd("sysctl -w net.ipv4.ip_no_pmtu_disc=1")

    # Disable TCP MTU probing
    h1.cmd("sysctl -w net.ipv4.tcp_mtu_probing=0")
    h2.cmd("sysctl -w net.ipv4.tcp_mtu_probing=0")

    info("*** Comenzando Red\n")
    net.start()

    # Configurar MTU en las interfaces del router
    h1.cmd("ifconfig h1-eth1 mtu 1500")
    h2.cmd("ifconfig h2-eth1 mtu 1500")
    router.cmd("ifconfig r1-eth1 mtu 1500")
    router.cmd("ifconfig r1-eth2 mtu 500")

    info("*** Comenzando terminales para server y h2 con xterm\n")
    makeTerms([h1, h2], term="xterm")

    info("*** Comenzando CLI\n")
    CLI(net)

    info("*** Frenando la Red al hacer exit\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    fragTopology()
