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

"""Handles all the apps being used, their registration etc."""
import logging


from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import handler
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.ofproto import ofproto_v1_3

from susan.apps import dhcp
from susan.apps import datapath
from susan.common import constants
from susan.common import packet as packet_util


LOG = logging.getLogger(__name__)


class AppManager(app_manager.RyuApp):
    """Takes care of all the applications and management of them."""
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(AppManager, self).__init__(*args, **kwargs)
        self.datapaths = set()
        self.apps = []

    def _add_datapath(self, dp):
        (host, port) = dp.address
        if dp.id not in self.datapaths:
            datapath.Datapath().add_datapath(dp.id, host, port)
            self.datapaths.add(dp.id)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, handler.CONFIG_DISPATCHER)
    def switch_features_handler(self, event):
        """Called when feature negotiation takes place. and adds necessary
           flows for the application.
        """
        datapath = event.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        self._add_datapath(datapath)
        packet_util.send_to_controller(parser=parser,
                                       ofproto=ofproto,
                                       datapath=datapath,
                                       priority=0,
                                       table_id=constants.TABLE.DEFAULT)

        req = parser.OFPSetConfig(datapath, ofproto_v1_3.OFPC_FRAG_REASM,
                                  ofproto.OFPCML_NO_BUFFER)

        datapath.send_msg(req)
        self.apps.append((dhcp.DHCP.matcher,
                          dhcp.DHCP(datapath).process_packet))

    def register(self, match, callback):
        """Registers an application to be managed by AppManager"""
        self.apps.append((match, callback))

    def classifier(self, pkt, datapath, in_port):
        """Classify a packet and forward to corresponding application"""
        for match, callback in self.apps:
            if match(pkt):
                callback(pkt, datapath, in_port)

            break

    @set_ev_cls(ofp_event.EventOFPPacketIn, handler.MAIN_DISPATCHER)
    def packet_in_handler(self, event):
        """Called on packet arrival and calls the correct apps."""
        pkt = packet.Packet(event.msg.data)
        try:
            self.classifier(pkt, event.msg.datapath,
                            event.msg.match['in_port'])
        except Exception:
            # Keep working normally if a packet processing fails, to process
            # next packets.
            LOG.error("Failure in processing packet", exc_info=True)
