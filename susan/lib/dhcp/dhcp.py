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
from abc import ABCMeta
from abc import abstractmethod
import struct

import six

from ryu.lib.packet import dhcp
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4

from susan.lib.dhcp import constants as dhcp_const
from susan.lib.dhcp import pack_option
from susan.common import constants as const
from susan.common import matcher
from susan.common import packet as packet_util
from susan.common import utils


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


@six.add_metaclass(ABCMeta)
class DHCPServer(object):
    """Handles all type of dhcp packets"""
    def __init__(self, datapath, *args, **kwargs):
        super(DHCPServer, self).__init__(*args, **kwargs)
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
        msg_type = dhcp_const.OPTIONS.MESSAGE_TYPE
        discover = struct.pack('!B', dhcp_const.REQUEST.DISCOVER)
        request = struct.pack('!B', dhcp_const.REQUEST.REQUEST)
        for option in opts:
            if option.tag == msg_type and option.value == discover:
                request_type = REQUEST_MAPPER.DHCPDISCOVER
                break
            elif option.tag == msg_type and option.value == request:
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
            return const.BROADCAST_IP
            # fixme(thenakliman): Fix this unicast
            # return pkt.ciaddr

    @staticmethod
    def _get_dst_mac(pkt):
        if pkt.get_protocol(dhcp.dhcp).ciaddr == const.ZERO_IPADDR:
            return const.BROADCAST_MAC
        else:
            return const.BROADCAST_MAC
            # fixme(thenakliman): Fix this unicast
            # return pkt.get_packet(ethernet.ethernet).src_mac

    def fetch_option_for_offer(self, pkt, datapath, in_port):
        opts = [dhcp.option(tag=dhcp_const.OPTIONS.MESSAGE_TYPE,
                            value=struct.pack('B', dhcp_const.REQUEST.OFFER))]
        opts.extend(self.fetch_options(pkt, datapath, in_port))
        return dhcp.options(opts)

    def fetch_option_for_ack(self, pkt, datapath, in_port):
        opts = [dhcp.option(tag=dhcp_const.OPTIONS.MESSAGE_TYPE,
                            value=struct.pack('B', dhcp_const.REQUEST.ACK))]
        opts.extend(self.fetch_options(pkt, datapath, in_port))
        return dhcp.options(opts)

    def fetch_options(self, pkt, datapath, in_port):
        dhcp_pkt = pkt.get_protocol(dhcp.dhcp)
        requested_params = None
        for option in dhcp_pkt.options.option_list:
            if option.tag == dhcp_const.OPTIONS.PARAMETER_REQUEST:
                requested_params = option.value
                break

        if requested_params is None:
            return []

        requested_params = struct.unpack('B' * len(requested_params),
                                         requested_params)

        host, datapath, in_port = datapath.address[0], datapath.id, in_port
        mac = self._get_mac(pkt)
        lease_time = self.get_lease_time(datapath, in_port, mac)
        option_list = [dhcp.option(tag=dhcp_const.OPTIONS.LEASE_TIME,
                                   value=struct.pack('!I', lease_time))]

        host_data = self.get_parameters(datapath, in_port, mac)
        for param in requested_params:
            value = host_data and host_data.get(param)
            if value:
                packed_value = pack_option.pack(param, value)
                option_list.append(dhcp.option(tag=param, value=packed_value))

        return option_list

    @abstractmethod
    def get_lease_time(self, host, datapath, in_port, mac):
        pass

    @abstractmethod
    def get_parameters(self, host, datapath, in_port, mac):
        pass

    @staticmethod
    def _make_dhcp_packet(operation, chaddr, xid, yiaddr,
                          siaddr, options=None):

        return dhcp.dhcp(op=operation, chaddr=chaddr,
                         xid=xid, yiaddr=yiaddr,
                         siaddr=siaddr,
                         options=options)

    def _send_dhcp_pkt(self, pkt, src_mac, dst_mac, src_ip, dst_ip,
                       src_port, dst_port, proto, options, datapath, out_port,
                       assigned_ip):

        ether_pkt = pkt.get_protocol(ethernet.ethernet)
        host, datapath_id, in_port = datapath.address[0], datapath.id, out_port
        next_server_ip = self.get_next_server_ip(datapath_id, in_port)
        dhcp_packet = packet_util.make_l4_packet(
            src_mac=src_mac, dst_mac=dst_mac,
            src_ip=src_ip, dst_ip=dst_ip,
            src_port=src_port, dst_port=dst_port,
            proto=proto)

        dhcp_pkt = self._make_dhcp_packet(
            operation=dhcp.DHCP_BOOT_REPLY, chaddr=ether_pkt.src,
            xid=pkt.get_protocol(dhcp.dhcp).xid,
            yiaddr=assigned_ip, siaddr=next_server_ip,
            options=options)

        dhcp_packet.add_protocol(dhcp_pkt)
        packet_util.send_packet(datapath,
                                dhcp_packet,
                                out_port)

    @abstractmethod
    def get_available_ip(self, datapath, in_port, mac):
        pass

    @abstractmethod
    def get_next_server_ip(self, host, datapath, in_port):
        pass

    def send_offer(self, pkt, datapath, in_port):
        """Sends DHCP offer request"""
        options = self.fetch_option_for_offer(pkt, datapath, in_port)
        host, datapath_id = datapath.address[0], datapath.id
        src_mac, src_ip = self.get_dhcp_server_info(datapath_id, in_port)
        mac = self._get_mac(pkt)
        assigned_ip = self.get_available_ip(datapath_id, in_port, mac)
        self._send_dhcp_pkt(
            pkt=pkt,
            src_mac=src_mac,
            dst_mac=const.BROADCAST_MAC,
            src_ip=src_ip,
            dst_ip=const.BROADCAST_IP,
            src_port=dhcp_const.PORTS.SERVER_PORT,
            dst_port=dhcp_const.PORTS.CLIENT_PORT,
            proto=const.PROTOCOL.UDP,
            options=options,
            datapath=datapath,
            out_port=in_port,
            assigned_ip=assigned_ip)

        self.commit_ip(datapath_id, in_port, mac, assigned_ip)

    @abstractmethod
    def get_dhcp_server_info(self, host, datapath, in_port):
        pass

    @staticmethod
    def _get_mac(pkt):
        return pkt.get_protocol(ethernet.ethernet).src

    @staticmethod
    def _get_ip(pkt):
        return pkt.get_protocol(ipv4.ipv4).src

    def get_mac_ip(self, pkt):
        return self._get_mac(pkt), self._get_ip(pkt)

    def handle_request(self, pkt, datapath, in_port):
        """Handles DHCPREQUEST packet"""
        self.send_ack(pkt, datapath, in_port)

    def send_ack(self, pkt, datapath, in_port):
        """Make and send DHCPACK packet"""
        options = self.fetch_option_for_ack(pkt, datapath, in_port)
        dst_ip = self._get_dst_ip(pkt)
        dst_mac = self._get_dst_mac(pkt)
        src_ip = self._get_ip(pkt)
        src_mac = self._get_mac(pkt)
        assigned_ip = self.get_committed_ip(datapath.id, in_port, src_mac)
        self._send_dhcp_pkt(
            pkt=pkt,
            src_mac=src_mac,
            dst_mac=dst_mac,
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=dhcp_const.PORTS.SERVER_PORT,
            dst_port=dhcp_const.PORTS.CLIENT_PORT,
            proto=const.PROTOCOL.UDP,
            options=options,
            datapath=datapath,
            out_port=in_port,
            assigned_ip=assigned_ip)
        self.reserve_ip(datapath.id, in_port, assigned_ip, src_mac)
