'''
Coursera:
- Software Defined Networking (SDN) course
-- Programming Assignment: Layer-2 Firewall Application

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta
'''

# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pox')))

from pox.core import core
from pox.openflow import libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
''' Add your imports here ... '''

import json
from pox.lib.packet import ethernet, ipv4, udp, tcp


log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]

''' Add your global variables here ... '''



class Firewall (EventMixin):

    def __init__ (self):
        
        self.rules = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        rules_path = os.path.join(dir_path, "rules.json")
        with open(rules_path, 'r') as f:
            self.rules = json.load(f)

        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")

    def build_match_from_rule(self, rule):
        match = of.ofp_match()
        if 'src_host' in rule:
            match.dl_src = EthAddr(rule['src_host'])
        if 'dst_host' in rule:
            match.dl_dst = EthAddr(rule['dst_host'])
        if 'protocol' in rule and rule['protocol'] != 'any':
            if rule['protocol'].lower() == 'tcp':
                match.nw_proto = 6
                match.dl_type = 0x800
            elif rule['protocol'].lower() == 'udp':
                match.nw_proto = 17
                match.dl_type = 0x800
        if 'dst_port' in rule:
            if 'protocol' in rule:
                if rule['protocol'].lower() == 'tcp':
                    match.tp_dst = int(rule['dst_port'])
                elif rule['protocol'].lower() == 'udp':
                    match.tp_dst = int(rule['dst_port'])
            else:
                match.tp_dst = int(rule['dst_port'])
        return match

    def _handle_ConnectionUp(self, event):
        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))
        for rule in self.rules:
            if rule['action'] != 'deny':
                continue
            match = self.build_match_from_rule(rule)
            msg = of.ofp_flow_mod()
            msg.match = match
            event.connection.send(msg)

    # def _handle_PacketIn(self, event):
    #     packet = event.parsed
    #     if not packet.parsed:
    #         log.warning("Ignoring incomplete packet")
    #         return

    #     ip_pkt = packet.find('ipv4')
    #     if ip_pkt is None:
    #         # No IP, no filtering
    #         return

    #     transport_pkt = ip_pkt.find('udp') or ip_pkt.find('tcp')

    #     src_mac = str(packet.src)
    #     dst_mac = str(packet.dst)
    #     proto = None
    #     dst_port = None

    #     if transport_pkt:
    #         proto = transport_pkt.__class__.__name__.lower()
    #         dst_port = transport_pkt.dstport

    #     for rule in self.rules:
    #         if rule['action'] != 'deny':
    #             continue

    #         if 'src_host' in rule and rule['src_host'].lower() != src_mac.lower():
    #             continue
    #         if 'dst_host' in rule and rule['dst_host'].lower() != dst_mac.lower():
    #             continue
    #         if 'protocol' in rule and rule['protocol'] != 'any' and rule['protocol'].lower() != proto:
    #             continue
    #         if 'dst_port' in rule and rule['dst_port'] != dst_port:
    #             continue

    #         log.info(f"Dropping packet: {src_mac} -> {dst_mac} (protocol={proto}, port={dst_port})")
    #         return  # Drop packet (no flow_mod = drop)

    #     # Si no matchea ninguna regla, reenviar (para pruebas podés usar flooding):
    #     # msg = of.ofp_packet_out()
    #     # msg.data = event.ofp
    #     # msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    #     # msg.in_port = event.port
    #     # event.connection.send(msg)


def launch ():
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall)
    # core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp )

""""
ConnectionUp
ConnectionDown
PortStatus
FlowRemoved
Statistics
Events
PacketIn
ErrorIn
BarrierIn
"""