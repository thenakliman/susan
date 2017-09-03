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

from susan.db import port as port_db
from susan.db.rdbms.models import port as port_model
from susan.db import rdbms


class Port(port_db.Port):
    def __init__(self, *args, **kwargs):
        super(Port, self).__init__(*args, **kwargs)

    @staticmethod
    def add_port(datapath_id, port, mac, subnet_id):
        session = rdbms.get_session()
        row = port_model.Port(datapath_id=datapath_id, port=port,
                              mac=mac, subnet_id=subnet_id)
        session.add(row)
        try:
            session.commit()
        except exc.IntegrityError:
            pass

    @staticmethod
    def update_port(id, host=None, port=None):
        pass

    @staticmethod
    def delete_port(datapath_id, subnet_id):
        session = rdbms.get_session()
        session.query(port_model.Port).filter_by(datapath_id=datapath_id,
                                                 subnet_id=subnet_id).delete()

    @staticmethod
    def get_port(datapath_id, port):
        session = rdbms.get_session()
        return session.query(port_model.Port).filter_by(
            datapath_id=datapath_id,
            port=port).one_or_none()
