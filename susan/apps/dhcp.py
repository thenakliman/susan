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

from susan.db.rdbms import dhcp as dhcp_db
from susan.lib.dhcp import dhcp
from susan.lib.dhcp import constants as const


# This class provides extra processing needs to be done for requirement
# specific processing.
class DHCP(dhcp.DHCPServer):
    def __init__(self, *args, **kwargs):
        super(DHCP, self).__init__(*args, **kwargs)
        self.db = dhcp_db.DHCPDB()

    def handle_discover(self, pkt, datapath, in_port):
        """Handle discover

           This method provides hooks for extra processing, needs to be done
           for specific to requirement. If no extra information is needed then
           call super method.
        """
        return super(DHCP, self).handle_discover(pkt, datapath, in_port)

    def handle_request(self, pkt, datapath, in_port):
        """Handle request

           This method provides hooks for extra processing, needs to be done
           for specific to requirement. If no extra information is needed then
           call super method.
        """
        return super(DHCP, self).handle_request(pkt, datapath, in_port)

    def get_available_ip(self, mac, ip, interface):
        """Gets the free available IP"""
        return '172.30.10.35'

    def get_subnet_id(self, host, datapath, interface):
        return self.db.get_subnet_id(host=host, datapath=datapath,
                                     interface=interface)

    def get_parameters(self, host, datapath, interface, mac):
        """Returns host data for the request"""
        subnet_id = self.get_subnet_id(host, datapath, interface)
        return self.db.get_parameter(subnet_id, mac)

    def get_dhcp_server_info(self, host, datapath, interface):
        """Returns mac and ip of the dhcp server being used"""
        subnet_id = self.get_subnet_id(host, datapath, interface)
        return self.db.get_dhcp_server_info(subnet_id)

    def get_next_server_ip(self, host, datapath, interface):
        "Get next server ip"""
        # FIXME(thenakliman)
        return '172.30.10.1'
        parameters = self.get_parameters(host, datapath, interface)
        return parameters.get(const.OPTIONS.TFTP_SERVER_NAME)

    def get_lease_time(self, host, datapath, interface, mac):
        """Get lease time for a host"""
        parameter = self.get_parameters(host, datapath, interface, mac)
        if parameter is None:
            return const.DEFAULT_LEASE_TIME

        return parameter.get(const.LEASE_TIME, const.DEFAULT_LEASE_TIME)
