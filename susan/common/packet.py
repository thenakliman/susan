from ryu.lib.packet import ether_types as ether
from ryu.lib.packet import ethernet, packet
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp


def send_packet(datapath, port, pkt):
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    actions = [parser.OFPActionOutput(port=ofproto.OFPP_FLOOD)]
    out = parser.OFPPacketOut(datapath=datapath,
                              buffer_id=ofproto.OFP_NO_BUFFER,
                              in_port=ofproto.OFPP_CONTROLLER,
                              actions=actions,
                              data=pkt)
    datapath.send_msg(out)



def get_ether_pkt(src, dst, ethertype=ether.ETH_TYPE_IP):
    """Creates a Ether packet"""
    return ethernet.ethernet(src=src, dst=dst, ethertype=ethertype)
    

def get_ip_pkt(src, dst, version=4, proto=0):
    """Creates a IP Packet"""
    return ipv4.ipv4(src=src, dst=dst, version=version, proto=proto)


def get_tcp_pkt(src_port, dst_port):
    """Creates a TCP Packet"""
    return tcp.tcp(src_port=src_port, dst_port=dst_port)


def get_udp_pkt(src_port, dst_port):
    """Creates a UDP Packet"""
    return udp.udp(src_port=src_port, dst_port=dst_port)


def get_pkt(protocols):
    """Create a packet if list of protocol packet is provided.
    """
    pkt = packet.Packet()
    for proto_pkt in protocols:
        pkt.add_protocol(proto_pkt)

    return pkt


def add_flow(datapath, priority, match, actions):
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                         actions)]

    mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                            match=match, instructions=inst)
    datapath.send_msg(mod)
