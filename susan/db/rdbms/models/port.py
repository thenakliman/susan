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
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Port(Base):
    __tablename__ = 'port'

    datapath_id = sa.Column(sa.String(64), sa.ForeignKey('reserved_ip.ip',
                                                         ondelete='CASCADE'),
                            primary_key=True)
    mac = sa.Column(sa.String(64), nullable=False)
    port = sa.Column(sa.String(10), nullable=False, primary_key=True)
    subnet_id = sa.Column(sa.String(36), sa.ForeignKey('subnet.id',
                                                       ondelete='CASCADE'),
                          nullable=False)
