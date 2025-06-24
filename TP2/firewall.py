from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr, IPAddr
import pox.lib.packet as pkt
from collections import namedtuple
import os
import json

log = core.getLogger()

CONFIG_FILE = "rules.json"
SWITCH_ID = 3  # ID del switch s3

FIELD_MAP = {
    "mac_src": "dl_src",            # Dirección MAC de origen
    "mac_dst": "dl_dst",            # Dirección MAC de destino
    "dl_type": "dl_type",           # Tipo de enlace de datos (por ejemplo, IPv4)
    "dl_vlan": "dl_vlan",           # VLAN ID
    "dl_vlan_pcp": "dl_vlan_pcp",   # Prioridad de VLAN
    "nw_src": "nw_src",             # Dirección IP de origen
    "nw_dst": "nw_dst",             # Dirección IP de destino
    "nw_proto": "nw_proto",         # Protocolo de red (17 para UDP, 6 para TCP, 1 para ICMP)
    "nw_tos": "nw_tos",             # Tipo de servicio de red
    "tp_src": "tp_src",             # Puerto de origen (TCP/UDP)
    "tp_dst": "tp_dst",             # Puerto de destino (TCP/UDP)
    "in_port": "in_port",           # Puerto de entrada
}

class Firewall(object):
    def __init__(self):        

        dir_path = os.path.dirname(os.path.realpath(__file__))
        rules_path = os.path.join(dir_path, CONFIG_FILE)
        with open(rules_path, 'r') as f:
            self.rules = json.load(f)
        
        for rule in self.rules:
            if "mac_src" in rule:
                rule["mac_src"] = EthAddr(rule["mac_src"])
            if "mac_dst" in rule:
                rule["mac_dst"] = EthAddr(rule["mac_dst"])

            if "nw_src" in rule:
                rule["nw_src"] = IPAddr(rule["nw_src"])
            if "nw_dst" in rule:
                rule["nw_dst"] = IPAddr(rule["nw_dst"])

        core.openflow.addListeners(self)

    def _handle_ConnectionUp(self, event):
        dpid = event.dpid
        log.info("Switch %s has connected", dpid)

        if dpid != SWITCH_ID:
            log.info("Ignoring switch %s", dpid)
            return

        for rule in self.rules:
            msg = of.ofp_flow_mod()
            match = of.ofp_match()

            uses_ip_fields = any(
                key in rule for key in ("nw_src", "nw_dst", "nw_proto", "tp_src", "tp_dst")
            )
            if uses_ip_fields:
                match.dl_type = pkt.ethernet.IP_TYPE # 0x0800 for IPv4 || 0x86DD for IPv6

            # Asignación dinámica de campos
            for rule_key, match_attr in FIELD_MAP.items():
                if rule_key in rule:
                    setattr(match, match_attr, rule[rule_key])
            msg.match = match

            if rule["action"] == "drop":
                msg.priority = 100
                msg.actions = []
                log.info("Installed DROP rule on switch %s: %s", dpid, match)
                event.connection.send(msg)

def launch():
    core.registerNew(Firewall)
