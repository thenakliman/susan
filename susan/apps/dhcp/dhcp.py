"""Process DHCP packet and provide IP address for the requests.

   Support Packet Types

   1. DHCPDISCOVER
   2. DHCP OFFER
   3. DHCP REQUEST
   4. DHCPACK

   Not supported

   1. DHCPNAK
   2. DHCPDECLINE
   3. DHCPRELEASE
   4. DHCPINFORM
"""
 
from ryu.lib.packet import packet
from ryu.lib.packet import dhcp
from ryu.lib.packet import ethertype

from susan.common import const
from susan.common import matcher
from susan.common import packet as packet_util
from susan.db import db


SERVER_IP = '172.30.10.1'
SERVER_MAC = ''
YIP = '172.30.10.10'

class DHCPRequest(object):
    """Defined type of requests to mapping name for DHCP protocol messages
    """
    DHCPDISCOVER = 'discover',
    DHCPOFFER = 'offer',
    DHCPREQUEST = 'request',
    DHCPACK = 'ack'


class DHCPServer(object):
    def __init__(self, *args, **kwargs):
        super(DHCPServer, self).__init__(*args, **kwargs)

    @staticmethod
    def matcher(pkt):
        return matcher.has_port(pkt=pkt, src_port=const.DHCP.CLIENT_PORT,
                                dst_port=const.DHCP.SERVER_PORT):

    @staticmethod
    def identify_packet(pkt):
        p = pkt.get_protocol(pkt)
        if p.siaddr != const.ZERO_IPADDR:
            return DHCPRequest.DHCPDISCOVER
        else:
            return DHCPRequest.DHCPREQUEST
         
    def process_packet(self, pkt):
        pkt_type = identify_packet(self, pkt)
        method_name = ("handle_%s" % pkt_type)
        getattr(self, method_name)(pkt)

    def handle_discover(self, pkt):
        self.send_offer(pkt)

    def send_offer(self, pkt):
        ether_pkt = pkt.get_protocol(ethernet.ethernet)
        # fixme(thenakliman) Add database layer for customized
        # IP assignment.
        # ipaddr = db.get_ip(ether_pkt.src)
        dhcp_pkt = dhcp.dhcp(op=2, chaddr=ether_pkt.src,
                             yiaddr=YIP,
                             siaddr=SERVER_IP)
        protocol_stacked = (
            packet_util.get_ether_pkt(src=SERVER_MAC, dst=const.BROADCAST_MAC),
            packet_util.get_ip_pkt(src=SERVER_IP, dst=const.BROADCAST_IP)
            packet_util.get_udp_pkt(src_port=DHCP.SERVER_PORT,
                                    dst_port=DHCP.CLIENT_PORT)
            dhcp_pkt)

        packet_util.send_packet(packet_util.get_pkt(protocol_stacked))

    def handle_request(self, pkt):
        self.send_ack(pkt)

    def send_ack(self, pkt):
        src_ether_pkt = pkt.get_protocol(ethernet.ethernet)
        src_ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        dhcp_pkt = dhcp.dhcp(op=2, chaddr=ether_pkt.src,
                             yiaddr=YIP,
                             siaddr=SERVER_IP)
        protocol_stacked = (
            packet_util.get_ether_pkt(src=SERVER_MAC, dst=const.BROADCAST_MAC),
            packet_util.get_ip_pkt(src=SERVER_IP, const.ZERO_IPADDR)
            packet_util.get_udp_pkt(src_port=DHCP.SERVER_PORT,
                                    dst_port=DHCP.CLIENT_PORT)
            dhcp_pkt)

        packet_util.send_packet(packet_util.get_pkt(protocol_stacked))
