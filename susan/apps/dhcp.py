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

import logging

from susan.common import exceptions
from susan.db.rdbms import dhcp as dhcp_db
from susan.lib.dhcp import dhcp
from susan.lib.dhcp import constants as const

LOG = logging.getLogger(__name__)


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
        LOG.info("Handling dhcp 'discover' from %s datapath on %s port",
                 datapath.id, in_port)
        return super(DHCP, self).handle_discover(pkt, datapath, in_port)

    def handle_request(self, pkt, datapath, in_port):
        """Handle request

           This method provides hooks for extra processing, needs to be done
           for specific to requirement. If no extra information is needed then
           call super method.
        """
        LOG.info("Handling dhcp 'Request' from %s datapath on %s port",
                 datapath.id, in_port)
        return super(DHCP, self).handle_request(pkt, datapath, in_port)

    def get_available_ip(self, datapath, interface):
        """Gets the free available IP"""

        ip = '172.30.10.35'
        LOG.info("Assigning %s ip for %s datapath %s port", ip,
                  datapath.id, interface)
        return ip

    def get_subnet_id(self, datapath, interface):
        try:
            subnet_id = self.db.get_subnet_id(datapath=datapath,
                                              interface=interface)
        except exceptions.SubnetNotDefinedException:
            LOG.error("%s port on %s datapath does not belong to any subnet.",
                      datapath.id, interface)

        return subnet_id

    def get_parameters(self, datapath, interface, mac):
        """Returns host data for the request"""
        try:
            subnet_id = self.get_subnet_id(datapath, interface)
        except exceptions.SubnetNotDefinedException:
            LOG.error("%s port on %s datapath does not belong to any subnet.",
                      interface=interface,
                      datapath=datapath,
                      mac=mac)

            raise ParameterNotFoundException(datapath_id=datapath.id,
                                             interface=interface,
                                             mac=mac)

        try:
            data = self.db.get_parameter(subnet_id, mac)
        except exceptions.ParameterNotFoundException:
            LOG.error("Patarameter for %s mac in %s subnet not found", mac, subnet_id)

        return data or dict()

    def get_dhcp_server_info(self, datapath, interface):
        """Returns mac and ip of the dhcp server being used"""
        try:
            subnet_id = self.get_subnet_id(datapath, interface)
        except exceptions.SubnetNotDefinedException:
            LOG.error("%s port on %s datapath does not belong to any subnet.",
                      datapath_id=datapath.id,
                      interface=interface,
                      mac=mac)

            raise ParameterNotFoundException(datapath_id=datapath.id,
                                             interface=interface,
                                             mac=mac)
        (dhcp_mac, dhcp_ip) = self.db.get_dhcp_server_info(subnet_id)
        return (dhcp_mac, dhcp_ip)

    def get_next_server_ip(self, datapath, interface):
        "Get next server ip"""
        # FIXME(thenakliman)
        return '172.30.10.1'
        parameters = self.get_parameters(host, datapath, interface)
        return parameters.get(const.OPTIONS.TFTP_SERVER_NAME)

    def get_lease_time(self, datapath, interface, mac):
        """Get lease time for a host"""
        parameter = self.get_parameters(datapath, interface, mac)
        return ((parameter and parameter.get(const.LEASE_TIME,
                                            const.DEFAULT_LEASE_TIME)
               ) or const.DEFAULT_LEASE_TIME)
