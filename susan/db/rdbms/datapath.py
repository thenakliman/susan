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

from susan.db import datapath as datapath_db
from susan.db.rdbms.models import datapath as dp_model
from susan.db import rdbms


class Datapath(datapath_db.Datapath):
    def __init__(self, *args, **kwargs):
        super(Datapath, self).__init__(*args, **kwargs)

    @staticmethod
    def add_datapath(id_, host, port):
        session = rdbms.get_session()
        row = dp_model.Datapath(id=id_, host=host, port=port)
        session.add(row)
        try:
            session.flush()
        except  exc.IntegrityError:
            pass

    @staticmethod
    def update_datapath(id, host=None, port=None):
        pass

    @staticmethod
    def delete_datapath(id_):
        session = rdbms.get_session()
        session.query(dp_model.Datapath).filter_by(id=id_).delete()

    @staticmethod
    def get_datapath(id_):
        session = rdbms.get_session()
        return session.query(dp_model.Datapath).filter_by(id=id_).one_or_none()
