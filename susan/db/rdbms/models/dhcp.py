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

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

Base = declarative_base()


class Subnet(Base):
    __tablename__ = 'subnet'

    id = sa.Column(sa.String(36), primary_key=True)
    network = sa.Column(sa.String(64), nullable=False)
    cidr = sa.Column(sa.Integer, nullable=False)
    gateway = sa.Column(sa.String(64), nullable=False)
    ip_range = relationship("IPRange", backref="subnet")
    # Currently only dhcp server per subnet is supported.
    # A subnet may not be have dhcp server therefore nullable is True.
    # It can create circular depencency if nullable is False is used.
    # Therefore we might not be able to add any entried.
    server = sa.Colun(sa.String(64), sa.ForeignKey('reserved_ip.ip',
                          ondelete='CASCADE'), nullable=True)


class IPRange(Base):
    __tablename__ = 'ip_range'

    
    id = sa.Column(sa.String(36), primary_key=True)
    subnet_id = sa.Column(sa.String(255), sa.ForeignKey('Subnet.id',
                          ondelete='CASCADE'), nullable=False)
    start_ip = sa.Column(sa.String(64), nullable=False)
    end_ip = sa.Column(sa.String(64), nullable=False)


class Parameter(Base):
    __tablename__ = 'parameter'
    subnet_id = sa.Column(sa.String(255), sa.ForeignKey('subnet.id',
                          ondelete='CASCADE'), nullable=False,
                          primary_key=True)

    mac_address = sa.Column(sa.String(32), sa.ForeignKey('ReservedIP.mac',
                                ondelete='CASCADE'), nullable=True,
                            primary_key=True)
    data = sa.Column(sa.PickleType, nullable=True, primary_key=True)
    mac = relationship("ReservedIP",
                       backref=backref("parameter", uselist=False))
    subnet = relationship("Subnet", backref=backref("parameter", uselist=False))


class ReservedIP(Base):
    __tablename__ = 'reserved_ip'
    ip = sa.Column(sa.String(64), nullable=False)
    mac = sa.Column(sa.String(64), nullable=False, primary_key=True)
    subnet_id = sa.Column(sa.String(255), sa.ForeignKey('subnet.id',
                              ondelete='CASCADE'), nullable=False,
                          primary_key=True)
    is_reserved = sa.Column(sa.Boolean(), nullable=False,
                            server_default=sa.sql.false())
    interface = sa.Column(sa.String(10), nullable=True)
    lease_time = sa.Column(sa.TIMESTAMP, nullable=True)
    renew_time = sa.Column(sa.TIMESTAMP, nullable=True)
    expiry_time = sa.Column(sa.TIMESTAMP, nullable=True)
    reserved_ip = relationship("ReservedIP", backref="subnet")
