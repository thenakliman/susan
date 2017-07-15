"""Contains code which matches different field of a packet."""

from ryu.lib.packet import tcp
from ryu.lib.packet import udp

def is_valid_port(port):
    """Validates whether a port is None or now"""
    return bool(port is not None)

def is_src_port(pkt, port):
    """Matches tcp/udp source port of a packet"""
    return is_valid_port(port) and (pkt.src_port == port)


def is_dst_port(pkt, port):
    """Matches tcp/udp destination port of a packet"""
    return is_valid_port(port) and (pkt.dst_port == port)


def has_port(pkt, src_port=None, dst_port=None):
    """Matches tcp/udp source and destination port"""
    l4_pkt = pkt.get_protocol(udp.udp) or pkt.get_protocol(tcp.tcp)
    if l4_pkt is None:
        return False

    return is_src_port(l4_pkt, src_port) and is_dst_port(l4_pkt, dst_port)
