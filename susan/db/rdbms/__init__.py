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

import importlib

from sqlalchemy import orm
import sqlalchemy as sa

from susan import CONF

SQL_SESSION = None


DRIVER_BASE = 'susan.db'


# TODO(thenakliman): Only connection is being established. There are no
# configuration's done except default. Features specific to database should
# be supported to utilize database capability effectively.
def create_engine(connection=None):
    global SQL_SESSION

    driver_name = CONF.get('default', 'database')
    if connection is None:
        driver = importlib("%s.%s", DRIVER_BASE, driver_name)
        connection = driver.get_connection_string()

    engine = sa.create_engine(connection, echo=True)
    SQL_SESSION = orm.sessionmaker(bind=engine, autocommit=True)


def get_session():
    if SQL_SESSION is None:
        create_engine()

    return SQL_SESSION()
