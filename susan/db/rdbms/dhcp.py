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

from sqlalchemy import exc
import uuid

from susan.common import exceptions
from susan.db import dhcp as dhcp_db
from susan.db.rdbms.models import dhcp as d_model
from susan.db.rdbms import datapath
from susan.db.rdbms import port
from susan.db import rdbms


class Subnet(dhcp_db.DHCPdb):
    def __init__(self):
        super(Subnet, self).__init__()

    def create_subnet(self, network, cidr, gateway=None, server=None):
        session = rdbms.get_session()
        id_ = uuid.uuid1()
        row = d_model.Subnet(id=id_, network=network,
                             cidr=cidr, gateway=gateway, server=server)
        session.add(row)
        try:
            session.flush()
        except exc.IntergrityError:
            pass

    def update_subnet(self, id_, network=None,
                      cidr=None, gateway=None, server=None):
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
        try:
            session.flush()
        except exc.IntegrityError:
            pass

    def update_range(self, subnet_id, start_ip=None, end_ip=None):
        pass

    @staticmethod
    def delete_range(subnet_id, start_ip, end_ip):
        session = rdbms.get_session()
        session.query(d_model.IPRange).filter_by(subnet_id=subnet_id,
                                                 start_ip=start_ip,
                                                 end_ip=end_ip).delete()

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
    def add_reserved_ip(ip, mac, subnet_id, is_reserved=True,
                        lease_time=None, renew_time=None, expire_time=None):
        session = rdbms.get_session()
        row = d_model.ReservedIP(ip=ip, mac=mac, subnet_id=subnet_id,
                                 state=state, interface=interface,
                                 is_reserved=is_reserved,
                                 lease_time=lease_time,
                                 expire_time=expire_time)

        session.add(row)
        try:
            session.flush()
        except exc.IntegrityError:
            pass

    def update_reserved_ip(self, mac, subnet_id, ip=None,
                           is_reserved=True, lease_time=None,
                           renew_time=None, expire_time=None):
        pass

    @staticmethod
    def get_reserved_ip(mac, subnet_id):
        session = rdbms.get_session()
        return session.query(d_model.ReservedIP).filter_by(
            mac=mac, subnet_id=subnet_id).one_or_none()


class Parameter(dhcp_db.DHCPdb):
    def __init__(self):
        super(Parameter, self).__init__()

    @staticmethod
    def add_parameter(subnet_id, mac=None, data=None):
        session = rdbms.get_session()
        row = d_model.Parameter(subnet_id=subnet_id, mac=mac, data=data)
        session.add(row)
        try:
            session.flush()
        except exc.IntegrityError:
            pass

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


class DHCPDB(Subnet, Range, ReservedIP, Parameter,
             datapath.Datapath, port.Port):

    def __init__(self):
        super(DHCPDB, self).__init__(*args, **kwargs)

    def release_ip(self, ip, subnet_id, mac):
        self.delete_reserved_ip(subnet_id, mac)

    def get_ip(self, datapath, in_port):
        return '172.30.10.35'

    def commit_ip(self, subnet_id, mac, ip):
        session = rdbms.get_session()
        row = self.get_reserved_ip(mac=mac, subnet_id=subnet_id)
        if row is None:
            self.add_reserved_ip(subnet_id=subnet_id, ip=ip, mac=mac)
        elif row.ip != ip:
            raise exceptions.AlreadyAssignedDiffIPException(subnet_id=subnet_id,
                                                            mac=mac, ip=ip)
        elif row.lease_time is not None:
            raise exceptions.AlreadyAssignedIPException(subnet_id=subnet_id,
                                                        mac=mac, ip=ip)

    def reserve_ip(self, ip, subnet_id, mac):
        row = self.get_reserved_ip(mac=mac, subnet_id=subnet_id)
        if row is None:
            self.add_reserve_ip(ip=ip, subnet_id=subnet_id, mac=mac)
        elif row.ip != ip:
            raise exceptions.AlreadyAssignedDiffIPException(subnet_id=subnet_id,
                                                            mac=mac, ip=ip)

    def get_dhcp_server_ip(self, subnet_id):
        row = self.get_subnet(subnet_id)
        if row is None:
            raise exceptions.SubnetNotFoundExceptions(subnet_id=subnet_id)

        return row.server

    def get_mac(self, subnet_id, ip):
        session = rdbms.get_session()
        row = session.query(d_model.ReservedIP).filter_by(
            ip=ip, subnet_id=subnet_id).one_or_none()

        if row is None:
            raise exceptions.MACNotFound(ip=ip, subnet_id=subnet_id)

        return row.mac

    def get_dhcp_server_info(self, subnet_id):
        dhcp_server_ip = self.get_dhcp_server_ip(subnet_id)
        if dhcp_server_ip is None:
            raise exceptions.DHCPNotFound(subnet_id)

        dhcp_server_mac = self.get_mac(subnet_id, dhcp_server_ip)
        return (dhcp_server_mac, dhcp_server_ip)

    def get_subnet_id(self, datapath, interface):
        row = self.get_port(datapath_id=datapath, port=interface)
        if row is None:
            raise exceptions.SubnetNotDefinedFoundExceptions(
                datapath_id=datapath,
                interface=interface)

        return row.subnet_id

    def get_parameter(self, subnet_id, mac):
        row = super(DHCPDB, self).get_parameter(subnet_id, mac)
        if row is None:
            raise exceptions.ParameterNotFoundException(subnet_id=subnet_id)

        return row.data
