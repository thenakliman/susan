from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.ofproto import ofproto_v1_0
import six

from susan.common import utils


#@six.add_metaclass(utils.Singleton)
class AppManager(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(AppManager, self).__init__(*args, **kwargs)
        self.apps = []

    def register(self, match, callback):
        self.apps.append((match, callback))

    def classifier(self, pkt):
        for match, callback in self.apps:
            if match():
                callback(pkt)

            break

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        pkt = packet.Packet(ev.msg.data)
        classifier(pkt)
