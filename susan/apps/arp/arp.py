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

from susan.common import constants
from susan.common import utils

from ryu.lib.packet import arp
from ryu.ofproto import ofproto_v1_3, nicira_ext


class ARPHandler(object):
    """Handles ARP Requests"""
    def __init__(self, datapath):
        super(ARPHandler, self).__init__() 

    @staticmethod
    def _make_match(ofp_parser, ip_addr):
        # todo(thenakliman): Make it in single statement
        match = ofp_parser.OFPMatch()
        match.set_dl_type(constants.ETHERTYPE.ARP)
        match.set_arp_opcode(arp.ARP_REQUEST)
        match.set_arp_tpa(utils.ipv4_text_to_int(ip_addr))
        return match

    @staticmethod
    def _get_actions(parser, dnat_mac, ip_addr, port):
        return [
            parser.NXActionRegMove(src_field='arp_sha',
                                   dst_field='arp_tha',
                                   n_bits=48),
            parser.NXActionRegMove(src_field='arp_spa',
                                   dst_field='arp_tpa',
                                   n_bits=32),
            parser.NXActionRegMove(src_field='eth_src',
                                   dst_field='eth_dst',
                                   n_bits=48),
            parser.OFPActionSetField(eth_src=dnat_mac),
            parser.OFPActionSetField(arp_sha=dnat_mac),
            parser.OFPActionSetField(arp_op=arp.ARP_REPLY),
            parser.OFPActionSetField(arp_spa=utils.ipv4_text_to_int(ip_addr)),
            parser.NXActionRegMove(src_field='reg6',
                                   dst_field='reg7',
                                   n_bits=32),
            parser.NXActionRegLoad(dst='in_port',
                                   ofs_nbits=nicira_ext.ofs_nbits(0, 31),
                                   value=0),
            parser.OFPActionOutput(port)]


    @classmethod
    def add_arp_responder(cls, datapath, dnat_mac,
                          ip_addr, port=None,
                          priority=0, table=0):
        """Add arp reponder flow for an entry"""

        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        match = cls._make_match(ofp_parser, ip_addr)
        if port is None:
            port = ofproto.OFPP_FLOOD

        actions = cls._get_actions(ofp_parser, dnat_mac, ip_addr, port)

        instructions = [
            ofp_parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)
        ]

        # todo(thenakliman): Make generic flow methods(add, delete etc)
        req = ofp_parser.OFPFlowMod(datapath, cookie=0,
                                    command=ofproto.OFPFC_ADD,
                                    idle_timeout=0, hard_timeout=0,
                                    priority=priority, buffer_id=4294967295,
                                    match=match, instructions=instructions)
        datapath.send_msg(req)
