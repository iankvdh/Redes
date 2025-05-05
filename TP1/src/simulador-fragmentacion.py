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
        self.cmd('sysctl net.ipv4.ip_forward=1')
        
    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=lo0')
        super(LinuxRouter, self).terminate()

def fragTopology():
    net = Mininet(controller=OVSController, link=TCLink)
    
    info('*** Agregando Controlador\n')
    net.addController('c0')
    
    info('*** Agregando Hosts\n')
    h1 = net.addHost('h1', ip='192.168.1.2/24', defaultRoute='via 192.168.1.1')
    h2 = net.addHost('h2', ip='192.168.2.2/24', defaultRoute='via 192.168.2.1')
    
    info('*** Agregando Switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    
    info('*** Agregando Router\n')
    router = net.addHost('r1', cls=LinuxRouter, ip='192.168.1.1/24')
    
    info('*** Creando Links\n')
    # Enlace normal entre h1 y s1
    # h1 --1500-- s1 --1500-- r1 --600-- s2 --1500-- h2
    net.addLink(h1, s1)

    net.addLink(s1, router, intfName2='r1-eth1', 
               params2={'ip': '192.168.1.1/24'})
    
    net.addLink(router, s2, intfName1='r1-eth2',
               params1={'ip': '192.168.2.1/24'}) #,               cls=TCLink, mtu=500
    
    # Enlace normal entre s2 y h2 con perdida de paquetes al 10%
    net.addLink(s2, h2, loss = 25)

    h1.cmd("sysctl -w net.ipv4.ip_no_pmtu_disc=1")
    h2.cmd("sysctl -w net.ipv4.ip_no_pmtu_disc=1")
    
    info('*** Comenzando Red\n')
    net.start()
    
    # Configurar MTU en las interfaces del router
    # router.cmd('ifconfig r1-eth2 mtu 500')
    
    info('*** Comenzando terminales para h1 y h2 con xterm\n')
    makeTerms([h1, h2], term='xterm')


    info('*** Comenzando CLI\n')
    CLI(net)
    
    info('*** Frenando la Red al hacer exit\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    fragTopology()