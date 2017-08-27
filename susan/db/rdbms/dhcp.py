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

from susan.db import dhcp as dhcp_db
from susan.db.rdbms.models import dhcp as d_model
from susan.db import rdbms


class Subnet(dhcp_db.DHCPdb):
    def __init__(self):
        super(Subnet, self).__init__()

    def create_subnet(self, network, cidr, gateway=None):
        session = rdbms.get_session()
        row = d_model.Subnet(network=network, cidr=cidr, gateway=gateway)
        session.add(row)
        session.flush()

    def update_subnet(self, id_, network=None, cidr=None, gateway=None):
        pass

    def delete_subnet(self, id_):
        session = rdbms.get_session()
        session.query(d_model.Subnet).filter_by(id=id_).delete()

    @staticmethod
    def get_subnet(id_):
        session = rdbms.get_session()
        return session.query(d_model.Subnet).filter_by(id=id_).one_or_none()


class Range(dhcp_db.DHCPdb):
    def __init__(self):
        super(Range, self).__init__()

    def create_range(self, subnet_id, start_ip, end_ip):
        session = rdbms.get_session()
        row = d_model.IPRange(subnet_id=subnet_id, start_ip=start_ip,
                              end_ip=end_ip)
        session.add(row)
        session.flush()

    def update_range(self, subnet_id, start_ip=None, end_ip=None):
        pass

    @staticmethod
    def delete_range(subnet_id):
        d_model.IPRange(d_model.IPRange).filter_by(subnet_id=subnet_id).delete()

    @staticmethod
    def get_range(subnet_id, start_ip, end_ip):
        session = rdbms.get_session()
        return session.query(d_model.IPRange).filter_by(subnet_id=subnet_id,
                                                        start_ip=start_ip,
                                                        end_ip=end_ip)


class ReservedIP(dhcp_db.DHCPdb):
    def __init__(self):
        super(ReservedIP, self).__init__()

    @staticmethod
    def delete_reserved_ip(mac, subnet_id):
        session = rdbms.get_session()
        session.query(d_model.ReservedIP).filter_by(
            mac=mac,
            subnet_id=subnet_id).delete()

    @staticmethod
    def add_reserved_ip(ip, mac, subnet_id, state,
                        interface, is_reserved=True, lease_time=None,
                        renew_time=None, expire_time=None):
        session = rdbms.get_session()
        row = d_model.ReservedIP(ip=ip, mac=mac, subnet_id=subnet_id,
                                 state=state, interface=interface,
                                 is_reserved=is_reserved,
                                 lease_time=lease_time,
                                 expire_time=expire_time)

        session.add(row)
        session.flush()

    def update_reserved_ip(self, mac, subnet_id, ip=None,
                           interface=None, is_reserved=True, lease_time=None,
                           renew_time=None, expire_time=None):
        pass

    @staticmethod
    def get_reserved_ip(mac, subnet_id, interface):
        session = rdbms.get_session()
        return session.query(d_model.ReservedIP).filter_by(
            mac=mac, subnet_id=subnet_id, interface=interface).one_or_none()


class Parameter(dhcp_db.DHCPdb):
    def __init__(self):
        super(Parameter, self).__init__()

    @staticmethod
    def add_parameter(subnet_id, mac=None, data=None):
        session = rdbms.get_session()
        row = d_model.Parameter(subnet_id=subnet_id, mac=mac, data=data)
        session.add(row)
        session.flush()

    @staticmethod
    def delete_parameter(subnet_id, mac):
        session = rdbms.get_session()
        session.query(d_model.Parameter).filter_by(subnet_id=subnet_id,
                                                   mac=mac).delete()

    def update_parameter(self, subnet_id, mac=None, data=None):
        pass

    @staticmethod
    def get_parameter(subnet_id, mac=None):
        session = rdbms.get_session()
        return session.query(d_model.Parameter).filter_by(
            subnet_id=subnet_id, mac=mac).one_or_none()

class DHCPDB(Subnet, Range, ReservedIP, Parameter):
    def __init__(self):
        super(DHCPDB, self).__init__()

    def release_ip(self, ip, subnet_id, mac):
        self.delete_reserved_ip(subnet_id, mac)

    def get_ip(self, host, datapath, in_port):
        return '172.30.10.35'

    def commit_ip(self, subnet_id, mac, ip):
        pass

    def reserve_ip(self, ip, subnet_id, mac):
        pass

    def get_dhcp_server_ip(self, subnet_id):
        row = self.get_subnet(subnet_id)
        return row.server

    def get_mac(self, subnet_id, ip):
        session = rdbms.get_session()
        row = session.query(d_model.ReservedIP).filter_by(
            ip=ip, subnet_id=subnet_id).one_or_none()

        return row.mac

    def get_dhcp_server_info(self, subnet_id):
        dhcp_server_ip = self.get_dhcp_server_ip(subnet_id)
        dhcp_server_mac = self.get_mac(subnet_id, dhcp_server_ip)
        return (dhcp_server_mac, dhcp_server_ip)

    def get_subnet_id(self, host, datapath, interface):
        row = self.get_datapath(host, datapath_id=datapath, interface=interface)
        try:
            return row.subnet_id
        except AttributeError:
            return None