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

from sqlalchemy import orm

SQL_SESSION = None


def create_engine(connection=None):
    global SQL_SESSION

    if connection is None:
        connection = "sqlite:////var/lib/sqlite/susan"

    engine = sa.create_engine(connection, echo=True)
    SQL_SESSION = orm.sessionmaker(bind=engine)


def get_session():
    return SQL_SESSION()
