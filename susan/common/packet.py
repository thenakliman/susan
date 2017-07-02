from ryu.lib.packet import ether_type as ether
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp


def send_packet(self, port, pkt):
    datapath = self.datapath
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    actions = [parser.OFPActionOutput(port=port)]
    out = parser.OFPPacketOut(datapath=datapath,
                              buffer_id=ofproto.OFP_NO_BUFFER,
                              in_port=ofproto.OFPP_CONTROLLER,
                              actions=actions,
                              data=pkt)
    datapath.send_msg(out)



def get_ether_pkt(src, dst, ethertype=ether.ETH_TYPE_IP):
    """Creates a Ether packet"""
    return ethernet.ethernet(src=src, dst=dst, ethertype=ethertype)
    

def get_ip_pkt(version=4, src, dst):
    """Creates a IP Packet"""
    return ipv4.ipv4(version=version, src, dst)


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
