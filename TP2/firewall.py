from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr, IPAddr
import pox.lib.packet as pkt
import os
import json

from protocol_codes import PROTOCOL_CODES

log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ["HOME"]

CONFIG_FILE = "rules.json"
FIREWALL_SWITCH_ID = 3  # ID del switch donde aplicar firewall (s3)

FIELD_MAP = {
    "mac_src": "dl_src",  # Dirección MAC de origen
    "mac_dst": "dl_dst",  # Dirección MAC de destino
    "dl_type": "dl_type",  # Tipo de enlace de datos (por ejemplo, IPv4)
    "dl_vlan": "dl_vlan",  # VLAN ID
    "dl_vlan_pcp": "dl_vlan_pcp",  # Prioridad de VLAN
    "nw_src": "nw_src",  # Dirección IP de origen
    "nw_dst": "nw_dst",  # Dirección IP de destino
    "nw_proto": "nw_proto",  # Protocolo de red (17 para UDP, 6 para TCP, 1 para ICMP)
    "nw_tos": "nw_tos",  # Tipo de servicio de red
    "tp_src": "tp_src",  # Puerto de origen (TCP/UDP)
    "tp_dst": "tp_dst",  # Puerto de destino (TCP/UDP)
    "in_port": "in_port",  # Puerto de entrada
}


class Firewall(object):
    def __init__(self):

        dir_path = os.path.dirname(os.path.realpath(__file__))
        rules_path = os.path.join(dir_path, CONFIG_FILE)
        with open(rules_path, "r") as f:
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

        # Aplicar reglas de firewall solo en el switch designado
        if dpid == FIREWALL_SWITCH_ID:
            self._install_firewall_rules(event)
            log.info("Installed firewall rules on switch %s", dpid)

    def _install_firewall_rules(self, event):
        """Instala las reglas de firewall en el switch designado"""
        for rule in self.rules:
            msg = of.ofp_flow_mod()
            match = of.ofp_match()

            uses_ip_fields = any(
                key in rule
                for key in ("nw_src", "nw_dst", "nw_proto", "tp_src", "tp_dst")
            )
            if uses_ip_fields:
                match.dl_type = pkt.ethernet.IP_TYPE  # 0x0800 for IPv4

            # Asignación dinámica de campos
            for rule_key, match_attr in FIELD_MAP.items():
                if rule_key in rule:
                    setattr(match, match_attr, rule[rule_key])
            msg.match = match

            if rule["action"] == "drop":
                msg.priority = 100
                msg.actions = []
                log.info("Installing DROP rule: %s", rule)
                event.connection.send(msg)

    def _handle_PacketIn(self, event):
        dpid = event.connection.dpid
        packet = event.parsed.find("ipv4")
        if not packet:
            return
        proto_name = PROTOCOL_CODES.get(packet.protocol, str(packet.protocol))
        log.info("Switch %s: %s %s -> %s", dpid, proto_name, packet.srcip, packet.dstip)


def launch():
    core.registerNew(Firewall)
