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
import netaddr

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

    def get_subnet_mac(self, datapath, port):
        try:
            subnet_id = self.db.get_subnet_id(datapath=datapath,
                                              interface=port)
        except exceptions.SubnetNotDefinedException:
            LOG.error("%s port on %s datapath does not belong to any subnet.",
                      port, datapath)
            raise

        return subnet_id, self.db.get_mac_from_port(datapath, port)

    def get_ip(self, datapath, port, mac):
        subnet_id = self.get_subnet_id(datapath, port)
        return self.db.get_reserve_ip(subnet_id=subnet_id, mac=mac)

    def reserve_ip(self, datapath_id, in_port, ip):
        subnet_id, mac = self.get_subnet_mac(datapath_id, in_port)
        self.db.reserve_ip(ip=ip, subnet_id=subnet_id, mac=mac)
        LOG.info("Reserving  %s ip for %s mac in %s subnet",
                 ip, subnet_id, mac)

    def get_committed_ip(self, datapath, port, mac):
        try:
            return self.get_ip(datapath, port, mac)
        except exceptions.CommittedIPNotFoundException:
            LOG.error("IP for %s port on %s datapath not found",
                      port, datapath)
            raise

    def get_available_ip(self, datapath, interface, mac):
        """Gets the free available IP"""
        try:
            reserved_ip = self.get_ip(datapath, interface, mac)
        except exceptions.CommittedIPNotFoundException:
            reserved_ip = None

        if reserved_ip:
            return reserved_ip
        else:
            subnet_id = self.get_subnet_id(datapath, interface)
            allocated_ips = self.db.get_reserved_ip_in_subnet(subnet_id)
            ranges = self.db.get_ranges_in_subnet(subnet_id)
            if not ranges:
                LOG.error("Ranges for %s subnet is not defined", subnet_id)
                raise exceptions.RangeNotFoundException(subnet_id=subnet_id)

            allocated_set = set()
            for allocated_ip in allocated_ips:
                allocated_set.add(int(netaddr.IPAddress(allocated_ip)))

            # TODO(thenakliman): Ranges can be merged to process effectlively
            for start, end in ranges:
                for ip in range(int(netaddr.IPAddress(start)),
                                int(netaddr.IPAddress(end))):
                    if ip not in allocated_set:
                        return str(netaddr.IPAddress(ip))

        LOG.error("IP Could not be found in %s subnet", subnet_id)
        raise exceptions.IPNotAvailableException(subnet_id=subnet_id)

    def get_subnet_id(self, datapath, interface):
        try:
            subnet_id = self.db.get_subnet_id(datapath=datapath,
                                              interface=interface)
        except exceptions.SubnetNotDefinedException:
            LOG.error("%d port on %s datapath does not belong to any subnet.",
                      datapath, interface)
            raise

        return subnet_id

    def get_parameters(self, datapath, interface, mac):
        """Returns host data for the request"""
        try:
            subnet_id = self.get_subnet_id(datapath, interface)
        except exceptions.SubnetNotDefinedException:
            LOG.error("%s interface on %s datapath does not belong to any "
                      "subnet.", interface, datapath)

            raise exceptions.ParameterNotFoundException(datapath_id=datapath,
                                                        port=interface,
                                                        mac=mac)

        try:
            return self.db.get_parameter(subnet_id, mac)
        except exceptions.ParameterNotFoundException:
            LOG.error("Patarameter for %s mac in %s subnet not found",
                      mac, subnet_id)
            return dict()

    def get_dhcp_server_info(self, datapath, interface):
        """Returns mac and ip of the dhcp server being used"""
        try:
            subnet_id = self.get_subnet_id(datapath, interface)
            (dhcp_mac, dhcp_ip) = self.db.get_dhcp_server_info(subnet_id)
        except exceptions.SubnetNotDefinedException:
            LOG.error("%s port on %s datapath does not belong to any subnet.",
                      datapath_id=datapath,
                      interface=interface,
                      mac=mac)

            raise exceptions.ParameterNotFoundException(
                datapath_id=datapath,
                interface=interface,
                mac=mac)

        return (dhcp_mac, dhcp_ip)

    def get_next_server_ip(self, datapath, interface):
        "Get next server ip"""
        try:
            return self.db.get_next_server(datapath, interface)
        except exceptions.NextServerNotDefinedException:
            LOG.error("Next server is not defined in %s subnet", subnet_id)
            raise

    def get_lease_time(self, datapath, interface, mac):
        """Get lease time for a host"""
        parameter = self.get_parameters(datapath, interface, mac)
        return ((parameter and parameter.get(const.OPTIONS.LEASE_TIME,
                                             const.DEFAULT_LEASE_TIME)
                 ) or const.DEFAULT_LEASE_TIME)

    def commit_ip(self, datapath_id, in_port, mac, ip):
        subnet_id = self.get_subnet_id(datapath=datapath_id,
                                       interface=in_port)
        self.db.commit_ip(subnet_id=subnet_id, mac=mac, ip=ip)
        LOG.info("Committed %s ip for %s mac in %s subnet", ip, mac, subnet_id)
