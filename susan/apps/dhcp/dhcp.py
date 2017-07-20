# Copyright 2017 <thenakliman@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import struct

from ryu.lib.packet import dhcp
from ryu.lib.packet import ethernet

from susan.apps.dhcp import constants as dhcp_const
from susan.common import constants as const
from susan.common import matcher
from susan.common import packet as packet_util
from susan.common import utils


SERVER_IP = '172.30.10.1'
NETMASK = '255.255.255.0'
SERVER_MAC = '16:b2:3b:34:24:77'
YIP = '172.30.10.10'
ROUTER = '172.30.10.1'
LEASE_TIME = 10000


REQUEST_MAPPER = utils.make_enum(
    DHCPDISCOVER='discover',
    DHCPOFFER='offer',
    DHCPREQUEST='request',
    DHCPACK='ack',
    DHCPNACK='nack',
    DHCPDECLINE='decline',
    DHCPRELEASE='release',
    DHCPINFORM='inform',
)


class DHCPServer(object):
    """Handles all type of dhcp packets"""
    def __init__(self, datapath):
        super(DHCPServer, self).__init__()
        self.initialize(datapath)

    @staticmethod
    def initialize(datapath):
        """Initialize DHCP application. It adds two flows
           1. Move DHCP packet to table defined in constant module.
           2. Move a DHCP Packet from DHCP table to controller.
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(eth_type=const.ETHERTYPE.IPV4,
                                ip_proto=const.PROTOCOL.UDP,
                                udp_src=dhcp_const.PORTS.CLIENT_PORT,
                                udp_dst=dhcp_const.PORTS.SERVER_PORT)

        instructions = [parser.OFPInstructionGotoTable(
            table_id=const.TABLE.DHCP)]

        packet_util.add_flow(datapath=datapath,
                             priority=10,
                             match=match,
                             table_id=const.TABLE.DEFAULT,
                             instructions=instructions)

        packet_util.send_to_controller(parser=parser,
                                       ofproto=ofproto,
                                       datapath=datapath,
                                       priority=0,
                                       table_id=const.TABLE.DHCP)

    @staticmethod
    def matcher(pkt):
        """Verify whether this packet is meant for this application or not"""

        return matcher.has_port(pkt=pkt,
                                src_port=dhcp_const.PORTS.CLIENT_PORT,
                                dst_port=dhcp_const.PORTS.SERVER_PORT)

    @staticmethod
    def identify_packet(pkt):
        """Identify type of DHCP packet"""

        dhcp_pkt = pkt.get_protocol(dhcp.dhcp)
        request_type = ''
        opts = dhcp_pkt.options.option_list
        for option in opts:
            if (option.tag == dhcp_const.OPTIONS.MESSAGE_TYPE and
                    option.value == struct.pack('B', dhcp_const.REQUEST.DISCOVER)):
                request_type = REQUEST_MAPPER.DHCPDISCOVER
                break
            elif (option.tag == dhcp_const.OPTIONS.MESSAGE_TYPE and
                  option.value == struct.pack('B', dhcp_const.REQUEST.REQUEST)):
                request_type = REQUEST_MAPPER.DHCPREQUEST
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
    def _get_dst_ip(pkt):
        if pkt.get_protocol(dhcp.dhcp).ciaddr == const.ZERO_IPADDR:
            return const.BROADCAST_IP
        else:
            return pkt.ciaddr

    @staticmethod
    def _get_dst_mac(pkt):
        if pkt.get_protocol(dhcp.dhcp).ciaddr == const.ZERO_IPADDR:
            return const.BROADCAST_MAC
        else:
            return pkt.get_packet(ethernet.ethernet).src_mac

    @staticmethod
    def send_offer(pkt, datapath, in_port):
        """Sends DHCP offer request"""
        ether_pkt = pkt.get_protocol(ethernet.ethernet)
        # fixme(thenakliman) Add database layer for customized
        # IP assignment.
        # ipaddr = db.get_ip(ether_pkt.src)
        option_list = [
            dhcp.option(tag=dhcp_const.OPTIONS.MESSAGE_TYPE,
                        value=struct.pack('B', dhcp_const.REQUEST.OFFER)),
            dhcp.option(tag=dhcp_const.OPTIONS.LEASE_TIME,
                        value=struct.pack('!', LEASE_TIME)),
            dhcp.option(tag=dhcp_const.OPTIONS.NETMASK,
                        value=utils.get_packed_address('255.255.255.0')),
            dhcp.option(tag=dhcp_const.OPTIONS.ROUTER,
                        value=utils.get_packed_address(ROUTER)),
            dhcp.option(tag=dhcp_const.OPTIONS.DNS_SERVER,
                        value=utils.get_packed_address('8.8.8.8')),
            dhcp.option(tag=dhcp_const.OPTIONS.SERVER_IDENTIFIER,
                        value=utils.get_packed_address(SERVER_IP))
        ]
        options = dhcp.options(option_list)
        dhcp_pkt = dhcp.dhcp(op=dhcp.DHCP_BOOT_REPLY, chaddr=ether_pkt.src,
                             xid=pkt.get_protocol(dhcp.dhcp).xid,
                             yiaddr=YIP,
                             siaddr=SERVER_IP,
                             options=options)

        protocol_stacked = (
            packet_util.get_ether_pkt(src=SERVER_MAC, dst=const.BROADCAST_MAC),
            packet_util.get_ip_pkt(src=SERVER_IP, dst=const.BROADCAST_IP, proto=17),
            packet_util.get_udp_pkt(src_port=dhcp_const.PORTS.SERVER_PORT,
                                    dst_port=dhcp_const.PORTS.CLIENT_PORT),
            dhcp_pkt)

        packet_util.send_packet(datapath, packet_util.get_pkt(protocol_stacked), in_port)

    def handle_request(self, pkt, datapath, in_port):
        """Handles DHCPREQUEST packet"""
        self.send_ack(pkt, datapath, in_port)

    @classmethod
    def send_ack(cls, pkt, datapath, port):
        """Make and send DHCPACK packet"""
        src_ether_pkt = pkt.get_protocol(ethernet.ethernet)
        option_list = [
            dhcp.option(tag=dhcp_const.OPTIONS.MESSAGE_TYPE,
                        value=struct.pack('B', dhcp_const.REQUEST.ACK)),
            dhcp.option(tag=dhcp_const.OPTIONS.LEASE_TIME,
                        value=struct.pack('I', LEASE_TIME)),
            dhcp.option(tag=dhcp_const.OPTIONS.NETMASK,
                        value=utils.get_packed_address(NETMASK)),
            dhcp.option(tag=dhcp_const.OPTIONS.REQUESTED_IP,
                        value=utils.get_packed_address(YIP)),
            dhcp.option(tag=dhcp_const.OPTIONS.SERVER_IDENTIFIER,
                        value=utils.get_packed_address(SERVER_IP)),
            dhcp.option(tag=dhcp_const.OPTIONS.ROUTER,
                        value=utils.get_packed_address(ROUTER)),
        ]

        options = dhcp.options(option_list)
        dhcp_pkt = dhcp.dhcp(op=dhcp.DHCP_BOOT_REPLY, chaddr=src_ether_pkt.src,
                             yiaddr=YIP,
                             xid=pkt.get_protocol(dhcp.dhcp).xid,
                             siaddr=SERVER_IP,
                             options=options)
        dst_ip = cls._get_dst_ip(pkt)
        dst_mac = cls._get_dst_mac(pkt)
        protocol_stacked = (
            packet_util.get_ether_pkt(src=SERVER_MAC, dst=dst_mac),
            packet_util.get_ip_pkt(src=SERVER_IP, dst=dst_ip, proto=17),
            packet_util.get_udp_pkt(src_port=dhcp_const.PORTS.SERVER_PORT,
                                    dst_port=dhcp_const.PORTS.CLIENT_PORT),
            dhcp_pkt)

        packet_util.send_packet(datapath, packet_util.get_pkt(protocol_stacked), port)
