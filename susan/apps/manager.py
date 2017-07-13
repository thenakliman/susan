from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import handler
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.ofproto import ofproto_v1_3
import six

from susan.apps.dhcp import dhcp
from susan.common import utils
from susan.common import packet as packet_util


class AppManager(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    def __init__(self, *args, **kwargs):
        super(AppManager, self).__init__(*args, **kwargs)
        self.apps = [(dhcp.DHCPServer.matcher, dhcp.DHCPServer().process_packet)]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, handler.CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        packet_util.add_flow(datapath, 0, match, actions)
        req = parser.OFPSetConfig(datapath, ofproto_v1_3.OFPC_FRAG_REASM,
                                  ofproto.OFPCML_NO_BUFFER)
        datapath.send_msg(req)


    def register(self, match, callback):
        self.apps.append((match, callback))

    def classifier(self, pkt, dp, in_port):
        for match, callback in self.apps:
            if match(pkt):
                callback(pkt, dp, in_port)

            break

    @set_ev_cls(ofp_event.EventOFPPacketIn, handler.MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        pkt = packet.Packet(ev.msg.data)
        if self.apps[0][0](pkt):
            #import pdb
            #pdb.set_trace()
            packet.Packet(ev.msg.data)

        self.classifier(pkt, ev.msg.datapath, ev.msg.match['in_port'])
