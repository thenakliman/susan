from ryu.lib.packet import udp


def is_src_port(pkt, port):
    return (pkt.src_port == port)


def is_dst_port(pkt, port):
    return (pkt.src_port == port)


def has_port(pkt, src_port=None, dst_port=None):
    p = pkt.get_protocol(udp.udp)

    if not p:
        return False

    return (((not src_port) or is_src_port(p, src_port)) and
            ((not dst_port) or is_dst_port(p, dst_port)))
