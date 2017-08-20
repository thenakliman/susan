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

import sqlalchemy as sa
import uuid

from susan.db import dhcp as dhcp_db
from susan.db.rdbms.models import dhcp as d_model


class Subnet(object):
    def __init__(self):
        pass

    def create_subnet(self, network, cidr, gateway=None):
        session = dhcp_db.get_session()
        row = d_model.Subnet(network=network, cidr=cidr, gateway=gateway)
        session.add(row)
        session.flush()

    def update_subnet(self, id_, network=None, cidr=None, gateway=None):
        pass

    def delete_subnet(self, id_):
        session = dhcp_db.get_session()
        session.query(d_model.Subnet).filter_by(id=_id).delete()

    def get_subnet(self, id_):
        return session.query(d_model.Subnet).filter_by(id=id_).one_or_none()


class Range(object):
    def __init__(self):
        pass

    def create_range(self,  subnet_id, start_ip, end_ip):
        session = dhcp_db.get_session()
        row = d_model.Range(subnet_id=subnet_id, start_ip=start_ip,
                            end_ip=end_ip)
        session.add(row)
        session.flush()

    def update_range(self, subnet_id, start_ip=None, end_ip=None):
        pass

    def delete_range(self, subnet_id):
        session = dhcp_db.get_session()
        d_model.Range(d_model.Range).filter_by(subnet_id=subnet_id).delete()

    def get_range(self, subnet_id, start_ip, end_ip):
        session = dhcp_db.get_session()
        return seesion.query(d_model.Range).filter_by(subnet_id=subnet_id,
                                                      start_ip=start_ip,
                                                      end_ip=end_ip)


class ReservedIP(object):
    def __init__(self):
        pass

    def delete_reserved_ip(self,  mac, subnet_id):
        session = dhcp_db.get_session()
        session.query(d_model.ReservedIP).filter_by(mac=mac,
            subnet_id=subnet_id).delete()


    def add_reserved_ip(self,  ip, mac, subnet_id, state,
                        interface, is_reserved=True, lease_time=None,
                        renew_time=None, expire_time=None):
        session = dhcp_db.get_session()
        row = d_model.ReservedIP(ip=ip, mac=mac, subnet_id=subnet_id,
                                 state=state, interface=interface,
                                 is_reserved=is_reserved,
                                 lease_time=lease_time,
                                 expire_time=expire_time)

        session.add()
        session.flush()

    def update_reserved_ip(self, mac, subnet_id, ip=None,
                           interface=None, is_reserved=True, lease_time=None,
                           renew_time=None, expire_time=None):
        pass

    def get_reserved_ip(self, mac, subnet_id):
        session = dhcp_db.get_session()
        return session.query(d_model.ReservedIP).filter_by(
            mac=mac, subnet_id=subnet_id).one_or_none()


class Parameter(object):
    def __init__(self):
        pass

    def create_parameter(self, subnet_id,
                         mac_address=None, data=None):
        session = dhcp_db.get_session()
        row = d_mode.Parameter(subnet_id=subnet_id, mac_address=mac, data=data)
        session.add(row)
        session.flush()

    def delete_parameter(self,  subnet_id, mac):
        session = dhcp_db.get_session()
        session.query(d_model.Parameter).filter_by(subnet_id=subnet_id,
                                                   mac_address=mac).delete()

    def update_parameter(self, subnet_id, mac=None, data=None):
        pass

    def get_parameter(self, subnet_id, mac=None):
        session = dhcp_db.get_session()
        return session.query(d_model.Parameter).filter_by(
            subnet_id=subnet_id, mac_address=mac).all()


class DHCPDB(Subnet, Range, ReservedIP, Data):
    def __init__(self, session):
        pass

    def release_ip(self, subnet_id, mac):
        self.delete_release_ip(subnet_id, mac)

    def get_ip(self, subnet_id, mac):
        pass

    def commit_ip(self, subnet_id, mac, ip):
        pass

    def reserve_ip(self, ip, subnet_id, mac):
        pass
