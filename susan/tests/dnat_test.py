from susan.apps.arp import arp
from susan.apps.dnat import dnat

from ryu.lib import addrconv
import struct
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, nicira_ext
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet


class ExampleSwitch13(app_manager.RyuApp):
  OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
  def __init__(self, *args, **kwargs):
    super(ExampleSwitch13, self).__init__(*args, **kwargs)
    # initialize mac address table.
    self.mac_to_port = {}

  @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
  def switch_features_handler(self, ev):
    datapath = ev.msg.datapath
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser

    # install the table-miss flow entry.
    match = parser.OFPMatch()
    actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
    ofproto.OFPCML_NO_BUFFER)]
    self.add_flow(datapath, match, actions)

  def add1_flow(self, datapath, priority, match, actions):
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    # construct flow_mod message and send it.
    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
            actions)]
    mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                            match=match, instructions=inst)
    datapath.send_msg(mod)

  @staticmethod
  def ipv4_text_to_int(ip_text):
        return struct.unpack('!I', addrconv.ipv4.text_to_bin(ip_text))[0]

  def add_flow(self, dp, match, actions):
        ofp = ofproto = dp.ofproto
        ofp_parser = parser = dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                actions)]
        req = ofp_parser.OFPFlowMod(dp, cookie=0,
                                    command=ofp.OFPFC_ADD,
                                    idle_timeout=0, hard_timeout=0,
                                    priority=0, buffer_id=4294967295,
                                    match=match, instructions=inst)

        dp.send_msg(req)
        dnat.DNAT().dnat(dp, 'ac:e0:10:fc:1f:0e', '192.168.4.153', 'b6:59:69:13:c6:db', '172.30.10.30', priority=10)


  @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
  def _packet_in_handler(self, ev):
    msg = ev.msg
    datapath = msg.datapath
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    # get Datapath ID to identify OpenFlow switches.
    dpid = datapath.id
    self.mac_to_port.setdefault(dpid, {})
    # analyse the received packets using the packet library.
    pkt = packet.Packet(msg.data)
    eth_pkt = pkt.get_protocol(ethernet.ethernet)
    dst = eth_pkt.dst
    src = eth_pkt.src
    # get the received port number from packet_in message.
    in_port = msg.match['in_port']
    self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
    # learn a mac address to avoid FLOOD next time.
    self.mac_to_port[dpid][src] = in_port
    # if the destination mac address is already learned,
    # decide which port to output the packet, otherwise FLOOD.
    if dst in self.mac_to_port[dpid]:
        out_port = self.mac_to_port[dpid][dst]
    else:
        out_port = ofproto.OFPP_FLOOD
    # construct action list.
    actions = [parser.OFPActionOutput(out_port)]
    # install a flow to avoid packet_in next time.
    if out_port != ofproto.OFPP_FLOOD:
        match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
        self.add_flow(datapath, match, actions)
    # construct packet_out message and send it.
    out = parser.OFPPacketOut(datapath=datapath,
    buffer_id=ofproto.OFP_NO_BUFFER,
    in_port=in_port, actions=actions,
    data=msg.data)
    datapath.send_msg(out)

