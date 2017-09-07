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

from susan.db import rdbms
from susan.db.rdbms import datapath as datapath_db


class Datapath(object):
    def __init__(self, *args, **kwargs):
        super(Datapath, self).__init__(*args, **kwargs)
        self.db = datapath_db.Datapath()

    def get_datapath(self, id_):
        session = rdbms.get_session()
        return self.db.get_datapath(session, id_)

    def add_datapath(self, id_, host, port):
        session = rdbms.get_session()
        self.db.add_datapath(session, id_, host, port)

    # May be this method is not required
    def delete_datapath(self, id_):
        pass

    def update_datapath(self, id_, host=None, port=None):
        session = rdbms.get_session()
        self.db.update_datapath(session, id_, host, port)
