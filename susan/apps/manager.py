"""Handles all the apps being used, their registration etc."""
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import handler
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.ofproto import ofproto_v1_3

from susan.apps.dhcp import dhcp
from susan.common import packet as packet_util


class AppManager(app_manager.RyuApp):
    """Takes care of all the applications and management of them."""
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    def __init__(self, *args, **kwargs):
        super(AppManager, self).__init__(*args, **kwargs)
        self.apps = [(dhcp.DHCPServer.matcher, dhcp.DHCPServer().process_packet)]

    # pylint: disable=no-member,no-self-use,locally-disabled
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, handler.CONFIG_DISPATCHER)
    def switch_features_handler(self, event):
        """Called when feature negotiation takes place. and adds necessary
           flows for the application.
        """
        datapath = event.msg.datapath
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
        """Registers an application to be managed by AppManager"""
        self.apps.append((match, callback))

    def classifier(self, pkt, datapath, in_port):
        """Classify a packet and forward to corresponding application"""
        for match, callback in self.apps:
            if match(pkt):
                callback(pkt, datapath, in_port)

            break

    # pylint: disable=no-member
    @set_ev_cls(ofp_event.EventOFPPacketIn, handler.MAIN_DISPATCHER)
    def packet_in_handler(self, event):
        """Called on packet arrival and calls the correct apps."""
        pkt = packet.Packet(event.msg.data)
        self.classifier(pkt, event.msg.datapath, event.msg.match['in_port'])
