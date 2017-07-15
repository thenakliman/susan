"""Ryu DHCP App"""

from ryu.lib.packet import dhcp
from ryu.lib.packet import ethernet

from susan.apps.dhcp import constants as dhcp_const
from susan.common import constants as const
from susan.common import matcher
from susan.common import packet as packet_util


SERVER_IP = '172.30.10.1'
SERVER_MAC = '16:b2:3b:34:24:77'
YIP = '172.30.10.10'
ROUTER = '172.30.10.1'

class DHCPServer(object):
    """Handles all type of dhcp packets"""
    def __init__(self, *args, **kwargs):
        super(DHCPServer, self).__init__(*args, **kwargs)

    @staticmethod
    def matcher(pkt):
        """Verify whether this packet is meant for this application or not"""

        return matcher.has_port(pkt=pkt, src_port=dhcp_const.DHCPPort.CLIENT_PORT,
                                dst_port=dhcp_const.DHCPPort.SERVER_PORT)

    @staticmethod
    def identify_packet(pkt):
        """Identify type of DHCP packet"""

        dhcp_pkt = pkt.get_protocol(dhcp.dhcp)
        request_type = ''
        opts = dhcp_pkt.options.option_list
        for option in opts:
            if option.tag == 53 and option.value == '\x01':
                request_type = dhcp_const.DHCPRequest.DHCPDISCOVER
                break
            elif option.tag == 53 and option.value == '\x03':
                request_type = dhcp_const.DHCPRequest.DHCPREQUEST
                break

        return request_type

    def process_packet(self, pkt, datapath, in_port):
        """Dispatch packet processing to method of this class"""
        pkt_type = self.identify_packet(pkt)
        method_name = ("handle_%s" % pkt_type)
        getattr(self, method_name)(pkt, datapath, in_port)

    def handle_discover(self, pkt, datapath, in_port):
        """Handles DHCP discover request"""
        self.send_offer(pkt, datapath, in_port)

    @staticmethod
    def send_offer(pkt, datapath, in_port):
        """Sends DHCP offer request"""
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
            packet_util.get_udp_pkt(src_port=dhcp_const.DHCPPort.SERVER_PORT,
                                    dst_port=dhcp_const.DHCPPort.CLIENT_PORT),
            dhcp_pkt)

        packet_util.send_packet(datapath, packet_util.get_pkt(protocol_stacked), in_port)

    def handle_request(self, pkt, datapath, in_port):
        """Handles DHCPREQUEST packet"""
        self.send_ack(pkt, datapath, in_port)

    @staticmethod
    def send_ack(pkt, datapath, port):
        """Make and send DHCPACK packet"""
        src_ether_pkt = pkt.get_protocol(ethernet.ethernet)
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
            packet_util.get_udp_pkt(src_port=dhcp_const.DHCPPort.SERVER_PORT,
                                    dst_port=dhcp_const.DHCPPort.CLIENT_PORT),
            dhcp_pkt)

        packet_util.send_packet(datapath, packet_util.get_pkt(protocol_stacked), port)
