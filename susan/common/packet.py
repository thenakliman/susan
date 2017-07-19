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
"""Contains common methods to create packets"""

from ryu.lib.packet import ether_types as ether
from ryu.lib.packet import ethernet, packet
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp

from susan.common import constants


def send_packet(datapath, pkt, port=None):
    """Send a packet to specified port and datapath"""
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    if port is None:
        port = ofproto.OFPP_FLOOD

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


def add_flow(datapath, match, actions=None, priority=0,
             table_id=constants.TABLE.DEFAULT, instructions=None):
    """Add flows to specified table."""

    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    instructions = instructions or []
    if actions:
        instructions.append(
            parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions))

    flow = parser.OFPFlowMod(datapath=datapath, priority=priority,
                             match=match, instructions=instructions,
                             table_id=table_id, command=ofproto.OFPFC_ADD)
    datapath.send_msg(flow)


def send_to_controller(parser, ofproto, datapath, table_id, priority=0):
    match = parser.OFPMatch()
    actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                      ofproto.OFPCML_NO_BUFFER)]

    add_flow(datapath=datapath, priority=priority,
             match=match, actions=actions, table_id=table_id)
