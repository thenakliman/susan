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
from susan.apps.arp import arp
from susan.common import constants
from susan.common import utils
from susan.common import packet as packet_util


class DNAT(object):
    def __init__(self):
        super(DNAT, self).__init__()

    @staticmethod
    def _get_match(parser, dst_mac, nat_ip):
        return parser.OFPMatch(eth_type=constants.ETHERTYPE.IPV4,
                               eth_dst=dst_mac,
                               ipv4_dst=nat_ip)

    @staticmethod
    def _get_actions(datapath, dst_mac, ip_addr, port=None):
        parser = datapath.ofproto_parser
        # dst_ipv4 = utils.get_packed_address(ip_addr)

        if port is None:
            port = datapath.ofproto.OFPP_FLOOD

        return [parser.OFPActionSetField(ipv4_dst=ip_addr),
                parser.OFPActionSetField(eth_dst=dst_mac),
                parser.NXActionRegLoad(dst='in_port',
                                       ofs_nbits=nicira_ext.ofs_nbits(0, 31),
                                       value=0),
                parser.OFPActionOutput(port)]

    @classmethod
    def dnat(cls, datapath, pub_mac, pub_ipaddr, private_mac, private_ipaddr,
             port=None, table_id=0, priority=0):

        parser = datapath.ofproto_parser
        arp.ARPHandler.add_arp_responder(datapath, pub_mac, pub_ipaddr)
        match = cls._get_match(parser, dst_mac=pub_mac, nat_ip=pub_ipaddr)
        actions = cls._get_actions(datapath, dst_mac=private_mac,
                                   ip_addr=private_ipaddr, port=port)

        instructions = [
            parser.OFPInstructionActions(datapath.ofproto.OFPIT_APPLY_ACTIONS,
                                         actions)
        ]

        packet_util.add_flow(datapath, match=match, instructions=instructions,
                             priority=priority, table_id=table_id)
