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

import struct
 
from ryu.lib.packet import packet
from ryu.lib.packet import dhcp, ipv4, ethernet, udp
# from ryu.lib.packet import ether_types

from susan.common import constants as const
from susan.common import matcher
from susan.common import packet as packet_util


SERVER_IP = '172.30.10.1'
SERVER_MAC = '16:b2:3b:34:24:77'
YIP = '172.30.10.10'
ROUTER = '172.30.10.1'
DHCP_FULL_PACK_SIZE = 86
DHCP_TRUNCATED_PACK_SIZE = 86

class DHCPRequest(object):
    """Defined type of requests to mapping name for DHCP protocol messages
    """
    DHCPDISCOVER = 'discover',
    DHCPOFFER = 'offer',
    DHCPREQUEST = 'request',
    DHCPACK = 'ack'


class DHCPServer(object):
    DHCP_TRUNCATED_PACK = '!BBBBIHH4s4s4s4s16s42s'
    DHCP_FULL_PACK = '!BBBBIHH4s4s4s4s16s64s128s'

    def __init__(self, *args, **kwargs):
        super(DHCPServer, self).__init__(*args, **kwargs)

    @staticmethod
    def matcher(pkt):
        return matcher.has_port(pkt=pkt, src_port=const.DHCP.CLIENT_PORT,
                                dst_port=const.DHCP.SERVER_PORT)

    @staticmethod
    def identify_packet(pkt):
        p = pkt.get_protocol(dhcp.dhcp)
        # import pdb
        # pdb.set_trace()
        request_type = ''
        opts = p.options.option_list
        for option in opts:
            if option.tag == 53 and option.value == '\x01':
                request_type = DHCPRequest.DHCPDISCOVER
                break
            elif option.tag == 53 and option.value == '\x03':
                request_type = DHCPRequest.DHCPREQUEST
                break

        return request_type

    def process_packet(self, pkt, dp, in_port):
        pkt_type = self.identify_packet(pkt)
        method_name = ("handle_%s" % pkt_type)
        getattr(self, method_name)(pkt, dp, in_port)

    def handle_discover(self, pkt, dp, in_port):
        self.send_offer(pkt, dp, in_port)

    def send_offer(self, pkt, dp, in_port):
        ether_pkt = pkt.get_protocol(ethernet.ethernet)
        # fixme(thenakliman) Add database layer for customized
        # IP assignment.
        # ipaddr = db.get_ip(ether_pkt.src)
        option_list = [
            dhcp.option(tag=53, value='\x02'),
            dhcp.option(tag=51, value='\x00\x00\xf1\x01')]
#
#            dhcp.option(tag=3, value=ROUTER),
#            dhcp.option(tag=1,value='255.255.255.0'),
#            dhcp.option(tag=51, value='86400s'),
#            dhcp.option(tag=6, value='8.8.8.8'),
#            dhcp.option(tag=54, value=SERVER_IP)
#        ]
        options = dhcp.options(option_list)
        dhcp_pkt = dhcp.dhcp(op=2, chaddr=ether_pkt.src,
                             xid=pkt.get_protocol(dhcp.dhcp).xid,
                             yiaddr=YIP,
                             siaddr=SERVER_IP,
                             options=options)
        protocol_stacked = (
            packet_util.get_ether_pkt(src=SERVER_MAC, dst=const.BROADCAST_MAC),
            packet_util.get_ip_pkt(src=SERVER_IP, dst=const.BROADCAST_IP, proto=17),
            packet_util.get_udp_pkt(src_port=const.DHCP.SERVER_PORT,
                                    dst_port=const.DHCP.CLIENT_PORT),
            dhcp_pkt)

        packet_util.send_packet(dp, in_port, packet_util.get_pkt(protocol_stacked))

    def handle_request(self, pkt, dp, in_port):
        self.send_ack(pkt, dp, in_port)

    def send_ack(self, pkt, dp, port):
        src_ether_pkt = pkt.get_protocol(ethernet.ethernet)
        src_ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        option_list = [
            dhcp.option(tag=53, value='\x05'),
            dhcp.option(tag=51, value='\x00\x00\xf1\x01')]
            # dhcp.option(tag=51, value='\xff')]
#            dhcp.option(tag=50, value=YIP),
#            dhcp.option(tag=54, value=SERVER_IP)
#        ]
        options = dhcp.options(option_list)
        dhcp_pkt = dhcp.dhcp(op=2, chaddr=src_ether_pkt.src,
                             yiaddr=YIP,
                             xid=pkt.get_protocol(dhcp.dhcp).xid,
                             siaddr=SERVER_IP,
                             options=options)
        protocol_stacked = (
            packet_util.get_ether_pkt(src=SERVER_MAC, dst=const.BROADCAST_MAC),
            packet_util.get_ip_pkt(src=SERVER_IP, dst=const.BROADCAST_IP, proto=17),
            packet_util.get_udp_pkt(src_port=const.DHCP.SERVER_PORT,
                                    dst_port=const.DHCP.CLIENT_PORT),
            dhcp_pkt)

        packet_util.send_packet(dp, port, packet_util.get_pkt(protocol_stacked))
