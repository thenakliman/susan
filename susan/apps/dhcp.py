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

from susan.lib.dhcp import dhcp


# This class provides extra processing needs to be done for requirement
# specific processing.
class DHCP(dhcp.DHCPServer):
    def __init__(self):
        pass

    def handle_discover(self, pkt, datapath, in_port):
        """Handle discover

           This method provides hooks for extra processing, needs to be done
           for specific to requirement. If no extra information is needed then
           call super method.
        """
        return super(DHCP, self).handle_offer(pkt, datapath, in_port)

    def handle_request(self, pkt, datapath, in_port):
        """Handle request

           This method provides hooks for extra processing, needs to be done
           for specific to requirement. If no extra information is needed then
           call super method.
        """
        return super(DHCP, self).handle_request(pkt, datapath, in_port)

    def get_ip(self, mac, ip):
        """Gets the free available IP"""
        return

    def get_parameters(mac, ip):
        """Returns host data for the request"""
        return

    def get_dhcp_server_info(self, subnet_id):
        """Returns mac and ip of the dhcp server being used"""
        return mac, ip

    def get_next_server(self, subnet_id):
        "Get next server ip"""
        return server_ip

    def get_lease_time(self, subnet_id):
        """Get lease time for a host"""
        return lease_time
