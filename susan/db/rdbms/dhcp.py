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
    def __init__(self, *args, **kwargs):
        super(Subnet, self).__init__(*args, **kwargs)

    @staticmethod
    def create_subnet(session, network, cidr, gateway=None,
                      server=None, next_server=None):

        id_ = str(uuid.uuid1())
        row = d_model.Subnet(id=id_, network=network,
                             cidr=cidr, gateway=gateway, server=server,
                             next_server=next_server)
        # TODO(thenakliman) it is never going to raise integrity excepion
        # due to conflicting is because id is being generated unique each time
        # this method is called.
        session.add(row)

    def update_subnet(self, id_, network=None,
                      cidr=None, gateway=None, server=None):
        pass

    @staticmethod
    def delete_subnet(session, id_):
        session.query(d_model.Subnet).filter_by(id=id_).delete()

    @staticmethod
    def get_subnet(session, id_):
        return session.query(d_model.Subnet).filter_by(id=id_).one_or_none()


class Range(dhcp_db.DHCPdb):
    def __init__(self, *args, **kwargs):
        super(Range, self).__init__(*args, **kwargs)

    @staticmethod
    def create_range(session, subnet_id, start_ip, end_ip):
        session = rdbms.get_session()
        row = d_model.IPRange(subnet_id=subnet_id, start_ip=start_ip,
                              end_ip=end_ip)
        session.add(row)

    def update_range(self, subnet_id, start_ip=None, end_ip=None):
        pass

    @staticmethod
    def delete_range(session, subnet_id, start_ip, end_ip):
        session.query(d_model.IPRange).filter_by(subnet_id=subnet_id,
                                                 start_ip=start_ip,
                                                 end_ip=end_ip).delete()

    @staticmethod
    def get_range(session, subnet_id):
        return session.query(d_model.IPRange).filter_by(
            subnet_id=subnet_id).all()


class ReservedIP(dhcp_db.DHCPdb):
    def __init__(self, *args, **Kwargs):
        super(ReservedIP, self).__init__()

    @staticmethod
    def delete_reserved_ip(session, mac, subnet_id):
        session.query(d_model.ReservedIP).filter_by(
            mac=mac,
            subnet_id=subnet_id).delete()

    @staticmethod
    def add_reserved_ip(session, ip, mac, subnet_id, is_reserved=True,
                        lease_time=None, renew_time=None, expiry_time=None):
        row = d_model.ReservedIP(ip=ip, mac=mac, subnet_id=subnet_id,
                                 is_reserved=is_reserved,
                                 lease_time=lease_time,
                                 expiry_time=expiry_time)

        session.add(row)

    def update_reserved_ip(self, mac, subnet_id, ip=None,
                           is_reserved=True, lease_time=None,
                           renew_time=None, expiry_time=None):
        pass

    @staticmethod
    def get_reserved_ip(session, mac, subnet_id):
        return session.query(d_model.ReservedIP).filter_by(
            mac=mac, subnet_id=subnet_id).one_or_none()

    @staticmethod
    def get_reserved_ip_of_subnet(session, subnet_id):
        return session.query(d_model.ReservedIP).filter_by(
            subnet_id=subnet_id).all()


class Parameter(dhcp_db.DHCPdb):
    def __init__(self, *args, **kwargs):
        super(Parameter, self).__init__(*args, **kwargs)

    @staticmethod
    def add_parameter(session, subnet_id, mac=None, data=None):
        row = d_model.Parameter(subnet_id=subnet_id, mac=mac, data=data)
        session.add(row)

    @staticmethod
    def delete_parameter(session, subnet_id, mac):
        session.query(d_model.Parameter).filter_by(subnet_id=subnet_id,
                                                   mac=mac).delete()

    def update_parameter(self, subnet_id, mac=None, data=None):
        pass

    @staticmethod
    def get_parameters(session, subnet_id, mac=None):
        return session.query(d_model.Parameter).filter_by(
            subnet_id=subnet_id, mac=mac).one_or_none()


class DHCPDB(Subnet, Range, ReservedIP, Parameter,
             datapath.Datapath, port.Port):

    def __init__(self, *args, **kwargs):
        super(DHCPDB, self).__init__(*args, **kwargs)

    def release_ip(self, ip, subnet_id, mac):
        session = rdbms.get_session()
        self.delete_reserved_ip(session, subnet_id, mac)
        session.commit()

    def commit_ip(self, subnet_id, mac, ip):
        session = rdbms.get_session()
        with session.begin():
            row = self.get_reserved_ip(session=session, mac=mac,
                                       subnet_id=subnet_id)
            if row is None:
                self.add_reserved_ip(session, subnet_id=subnet_id,
                                     ip=ip, mac=mac)
            elif row.ip != ip:
                raise exceptions.AlreadyAssignedDiffIPException(
                    subnet_id=subnet_id, mac=mac, ip=ip)
            elif row.lease_time is not None:
                raise exceptions.AlreadyAssignedIPException(
                    subnet_id=subnet_id, mac=mac, ip=ip)

    def reserve_ip(self, ip, subnet_id, mac):
        session = rdbms.get_session()
        with session.begin():
            row = self.get_reserved_ip(session=session, mac=mac,
                                       subnet_id=subnet_id)
            if row is None:
                self.add_reserved_ip(session=session, ip=ip,
                                     subnet_id=subnet_id, mac=mac)
            elif row.ip != ip:
                raise exceptions.AlreadyAssignedDiffIPException(
                    subnet_id=subnet_id, mac=mac, ip=ip)

    def get_dhcp_server_ip(self, session, subnet_id):
        row = self.get_subnet(session, subnet_id)
        try:
            return row.server
        except AttributeError:
            raise exceptions.SubnetNotFoundExceptions(subnet_id=subnet_id)

    # TODO(thenakliman): Don't fire the command directly, call subper class
    def get_mac(self, session, subnet_id, ip):
        row = session.query(d_model.ReservedIP).filter_by(
            ip=ip, subnet_id=subnet_id).one_or_none()

        try:
            return row.mac
        except AttributeError:
            raise exceptions.MACNotFound(ip=ip, subnet_id=subnet_id)

    def get_dhcp_server_info(self, subnet_id):
        session = rdbms.get_session()
        with session.begin():
            dhcp_server_ip = self.get_dhcp_server_ip(session, subnet_id)
            if dhcp_server_ip is None:
                raise exceptions.DHCPNotFound(subnet_id)

            dhcp_server_mac = self.get_mac(session, subnet_id, dhcp_server_ip)

        return (dhcp_server_mac, dhcp_server_ip)

    def get_subnet_id(self, datapath, port, session=None):
        if session is None:
            session = rdbms.get_session()

        row = self.get_port(session=session, datapath_id=datapath,
                            port=port)
        try:
            return row.subnet_id
        except AttributeError:
            raise exceptions.SubnetNotDefinedException(
                datapath_id=datapath,
                port=port)

    def get_parameter(self, subnet_id, mac=None):
        session = rdbms.get_session()
        with session.begin():
            row = self.get_parameters(session, subnet_id, mac)
            if row is None:
                row = self.get_parameters(session, subnet_id, None)

        try:
            return row.data
        except AttributeError:
            raise exceptions.ParameterNotFoundException(subnet_id=subnet_id)

    def get_next_server(self, datapath, port):
        session = rdbms.get_session()
        with session.begin():
            subnet_id = self.get_subnet_id(session=session, datapath=datapath,
                                           port=port)
            subnet = self.get_subnet(session, subnet_id)
        try:
            return subnet.next_server
        except AttributeError:
            raise exceptions.NextServerNotDefinedException(
                subnet_id=subnet_id)

    def get_ranges_in_subnet(self, subnet_id):
        session = rdbms.get_session()
        ranges = self.get_range(session, subnet_id)
        ip_ranges = []
        for ip_range in ranges:
            ip_ranges.append((ip_range.start_ip, ip_range.end_ip))

        return tuple(ip_ranges)

    def get_reserved_ip_in_subnet(self, subnet_id):
        session = rdbms.get_session()
        reserved_ips = self.get_reserved_ip_of_subnet(session, subnet_id)
        ips = []
        for ip in reserved_ips:
            ips.append(ip.ip)

        return tuple(ips)

    def get_mac_from_port(self, datapath_id, port):
        session = rdbms.get_session()
        port = self.get_port(session, datapath_id, port)
        try:
            return port.mac
        except AttributeError:
            raise exceptions.PortDoesNotExistException(datapath_id=datapath_id,
                                                       port=port)

    def get_reserve_ip(self, mac, subnet_id):
        session = rdbms.get_session()
        ip = self.get_reserved_ip(session=session, mac=mac,
                                  subnet_id=subnet_id)
        try:
            return ip.ip
        except AttributeError:
            raise exceptions.CommittedIPNotFoundException(mac=mac,
                                                          subnet_id=subnet_id)
