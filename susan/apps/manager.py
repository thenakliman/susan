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
from susan.common import app_utils
from susan.common import constants
from susan.common import graph_utils
from susan.common import packet as packet_util
from susan.pipeline import base as base_pipeline


LOG = logging.getLogger(__name__)


class AppManager(app_manager.RyuApp):
    """Takes care of all the applications and management of them."""
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(AppManager, self).__init__(*args, **kwargs)
        self.datapaths = set()
        self.pipeline = base_pipeline.get_pipeline()
        self.apps = []

    def _add_datapath(self, dp):
        (host, port) = dp.address
        if dp.id not in self.datapaths:
            datapath.Datapath().add_datapath(dp.id, host, port)
            self.datapaths.add(dp.id)

    # TODO(thenakliman): Needs to consider multiple datapaths and multi
    # tenancy. Multi tenancy seems to be big effort but exact method effort
    # can be assed later on. Atleast, now multiple datpaths needs to be
    # supported and thinked about.
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
        self.initialize_apps(datapath)

    def initialize_apps(self, datapath):
        pipeline = self.pipeline.get_pipeline()
        apps = graph_utils.get_apps(pipeline)
        for app in apps:
            if app == 'susan':
                # NOTE(thenakliman): Not sure whether it is a good idea or not
                # to consider susan as a special app. Other way to handle it
                # can be introduced if need arises
                continue
            # NOTE(thenakliman): We can receive ClassNotFound and AppNotFound
            # exceptions, they are not handled because we want to exit, if
            # such exception occured. Handling can be added only after
            # understanding real scenarios.
            app_module = self.pipeline.get_app_module(app)
            app_cls = self.pipeline.get_app_class(app)
            try:
                app = app_utils.load_app(app_module, app_cls)
            except AttributeError, ImportError:
                LOG.error("Unable to load %s app", exc_info=True)

            app.initialize(datapath)
            if app not in self.apps:
                self.apps.append(app(datapath))

    # TODO(thenakliman): This method is not being used, when we load the
    # application then it is expected that it is having **matcher and
    # **__call__** method defined. Other approach can be, to make applications
    # to register method for the events or table or processing. This way, we
    # avoid **matcher** and **__call__** protocol.
    def register(self, app):
        """Registers an application to be managed by AppManager"""
        self.apps.append(app)

    def classifier(self, pkt, datapath, in_port):
        """Classify a packet and forward to corresponding application"""
        for app in self.apps:
            # TODO(thenakliman): Currently each application provides, its
            # own matcher to match a packet therefore a packet has to
            # go through all the matchers defined, which can delay other
            # packet processing or reply to the received message. A better
            # Approach is needed, something like, each table process
            # a particular application therefore based on the table, packet
            # is forwarded to the correct application.
            if app.matcher(pkt):
                app(pkt, datapath, in_port)

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
