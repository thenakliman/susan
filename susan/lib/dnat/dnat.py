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

from ryu.ofproto import ofproto_v1_3, nicira_ext
from susan.lib.arp import arp
from susan.common import constants
from susan.common import packet as packet_util


class DNAT(object):
    def __init__(self):
        super(DNAT, self).__init__()

    @staticmethod
    def _get_ingress_match(parser, dst_mac, dst_ip):
        return parser.OFPMatch(eth_type=constants.ETHERTYPE.IPV4,
                               eth_dst=dst_mac,
                               ipv4_dst=dst_ip)

    @staticmethod
    def _get_egress_match(parser, src_mac, src_ip):
        return parser.OFPMatch(eth_type=constants.ETHERTYPE.IPV4,
                               eth_src=src_mac,
                               ipv4_src=src_ip)

    @staticmethod
    def _get_ingress_actions(datapath, dst_mac, ip_addr, port=None):
        parser = datapath.ofproto_parser

        if port is None:
            port = datapath.ofproto.OFPP_FLOOD

        return [parser.OFPActionSetField(ipv4_dst=ip_addr),
                parser.OFPActionSetField(eth_dst=dst_mac),
                parser.NXActionRegLoad(dst='in_port',
                                       ofs_nbits=nicira_ext.ofs_nbits(0, 31),
                                       value=0),
                parser.OFPActionOutput(port)]

    @staticmethod
    def _get_egress_actions(datapath, src_mac, ip_addr, port=None):
        parser = datapath.ofproto_parser

        if port is None:
            port = datapath.ofproto.OFPP_FLOOD

        return [parser.OFPActionSetField(ipv4_src=ip_addr),
                parser.OFPActionSetField(eth_src=src_mac),
                parser.NXActionRegLoad(dst='in_port',
                                       ofs_nbits=nicira_ext.ofs_nbits(0, 31),
                                       value=0),
                parser.OFPActionOutput(port)]

    @classmethod
    def _apply_ingress(cls, datapath, pub_mac, pub_ipaddr, private_mac,
                       private_ipaddr, port=None,
                       table_id=constants.TABLE.DNAT, priority=0):

        parser = datapath.ofproto_parser
        arp.ARPHandler.add_arp_responder(datapath, pub_mac, pub_ipaddr)
        match = cls._get_ingress_match(parser, dst_mac=pub_mac,
                                       dst_ip=pub_ipaddr)

        actions = cls._get_ingress_actions(datapath, dst_mac=private_mac,
                                           ip_addr=private_ipaddr, port=port)

        instructions = [
            parser.OFPInstructionActions(datapath.ofproto.OFPIT_APPLY_ACTIONS,
                                         actions)
        ]

        packet_util.add_flow(datapath, match=match, instructions=instructions,
                             priority=priority, table_id=table_id)

    @classmethod
    def _apply_egress(cls, datapath, pub_mac, pub_ipaddr, private_mac,
                      private_ipaddr, port=None,
                      table_id=constants.TABLE.DNAT, priority=0):

        parser = datapath.ofproto_parser
        match = cls._get_egress_match(parser, src_mac=private_mac,
                                      src_ip=private_ipaddr)

        actions = cls._get_egress_actions(datapath, src_mac=pub_mac,
                                          ip_addr=pub_ipaddr, port=port)

        instructions = [
            parser.OFPInstructionActions(datapath.ofproto.OFPIT_APPLY_ACTIONS,
                                         actions)
        ]

        packet_util.add_flow(datapath, match=match, instructions=instructions,
                             priority=priority, table_id=table_id)

    @classmethod
    def dnat(cls, datapath, pub_mac, pub_ipaddr, private_mac, private_ipaddr,
             port=None, table_id=constants.TABLE.DNAT, priority=0):

        cls._apply_ingress(datapath, pub_mac, pub_ipaddr, private_mac,
                           private_ipaddr, port, table_id, priority)

        cls._apply_egress(datapath, pub_mac, pub_ipaddr, private_mac,
                          private_ipaddr, port, table_id, priority)
