from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr

log = core.getLogger()

# Reglas: una lista de diccionarios, cada uno representa una regla de firewall
FIREWALL_RULES = [
    {
        "src_mac": EthAddr("00:00:00:00:01:01"),
        "dst_mac": EthAddr("00:00:00:00:01:03"),
        "action": "drop",
    },
    {
        "src_mac": EthAddr("00:00:00:00:01:03"),
        "dst_mac": EthAddr("00:00:00:00:01:01"),
        "action": "drop",
    },
    {
        "src_mac": EthAddr("00:00:00:00:01:01"),
        "tp_dst": 5001,
        "nw_proto": 17,  # UDP
        "action": "drop",
    },
    {
        "tp_dst": 80,
        "nw_proto": 6,  # TCP
        "action": "drop",
    },
    {
        "tp_dst": 80,
        "nw_proto": 17,  # UDP
        "action": "drop",
    },
]


class Firewall(object):
    def __init__(self):
        core.openflow.addListeners(self)

    def _handle_ConnectionUp(self, event):
        dpid = event.dpid
        log.info("Switch %s has connected", dpid)

        for rule in FIREWALL_RULES:
            msg = of.ofp_flow_mod()
            match = of.ofp_match()

            uses_ip_fields = any(
                key in rule
                for key in ("nw_src", "nw_dst", "nw_proto", "tp_src", "tp_dst")
            )
            if uses_ip_fields:
                match.dl_type = 0x0800

            # Seteo dinámico de campos
            if "src_mac" in rule:
                match.dl_src = rule["src_mac"]
            if "dst_mac" in rule:
                match.dl_dst = rule["dst_mac"]
            if "nw_src" in rule:
                match.nw_src = rule["nw_src"]
            if "nw_dst" in rule:
                match.nw_dst = rule["nw_dst"]
            if "nw_proto" in rule:
                match.nw_proto = rule["nw_proto"]
            if "tp_src" in rule:
                match.tp_src = rule["tp_src"]
            if "tp_dst" in rule:
                match.tp_dst = rule["tp_dst"]
            if "in_port" in rule:
                match.in_port = rule["in_port"]

            msg.match = match

            if rule["action"] == "drop":
                msg.priority = 100
                msg.actions = []  # sin acciones = drop
                log.info("Installed DROP rule on switch %s: %s", dpid, match)
                event.connection.send(msg)


def launch():
    core.registerNew(Firewall)
