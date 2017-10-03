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
from sqlalchemy import orm

from susan.db.rdbms import models


class Subnet(models.Base):
    __tablename__ = 'subnet'

    id = sa.Column(sa.String(36), primary_key=True)
    network = sa.Column(sa.String(64), nullable=False)
    cidr = sa.Column(sa.Integer, nullable=False)
    gateway = sa.Column(sa.String(64), nullable=False)
    next_server = sa.Column(sa.String(64), nullable=False)
    # Currently only dhcp server per subnet is supported.
    # A subnet may not be have dhcp server therefore nullable is True.
    # It can create circular depencency if nullable is False is used.
    # Therefore we might not be able to add any entried.
    server = sa.Column(sa.String(64), sa.ForeignKey('reserved_ip.ip',
                                                    ondelete='CASCADE'),
                       nullable=True)
    ip_range = orm.relationship("IPRange")


class IPRange(models.Base):
    __tablename__ = 'ip_range'

    subnet_id = sa.Column(sa.String(36), sa.ForeignKey('subnet.id',
                                                       ondelete='CASCADE'),
                          nullable=False, primary_key=True)
    start_ip = sa.Column(sa.String(64), nullable=False, primary_key=True)
    end_ip = sa.Column(sa.String(64), nullable=False, primary_key=True)


class Parameter(models.Base):
    __tablename__ = 'parameter'

    subnet_id = sa.Column(sa.String(36), sa.ForeignKey('subnet.id',
                                                       ondelete='CASCADE'),
                          nullable=False, primary_key=True)

    # IP has to be reserved for other keys, if want to fetch parameters
    # based on mac
    mac = sa.Column(sa.String(32), sa.ForeignKey('port.mac',
                                                 ondelete='CASCADE'),
                    nullable=True, primary_key=True)

    data = sa.Column(sa.PickleType, nullable=True)


class ReservedIP(models.Base):
    __tablename__ = 'reserved_ip'

    ip = sa.Column(sa.String(64), nullable=False)
    mac = sa.Column(sa.String(32), nullable=False, primary_key=True)
    subnet_id = sa.Column(sa.String(36), sa.ForeignKey('subnet.id',
                                                       ondelete='CASCADE'),
                          nullable=False, primary_key=True)

    is_reserved = sa.Column(sa.Boolean(), nullable=False,
                            server_default=sa.sql.false())
    lease_time = sa.Column(sa.TIMESTAMP, nullable=True)
    renew_time = sa.Column(sa.TIMESTAMP, nullable=True)
    expiry_time = sa.Column(sa.TIMESTAMP, nullable=True)
    subnet = orm.relationship('Subnet', foreign_keys=[subnet_id])
