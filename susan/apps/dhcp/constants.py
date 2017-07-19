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


# =============================================
# DHCP constants
# =============================================
# pylint: disable=too-few-public-methods

from susan.common import utils


PORTS = utils.make_enum(
    CLIENT_PORT=68,
    SERVER_PORT=67
)


OPTIONS = utils.make_enum(
    NETMASK=1,
    DNS_SERVER=6,
    ROUTER=3,
    MTU=26,
    REQUESTED_IP=50,
    LEASE_TIME=51,
    MESSAGE_TYPE=53,
    SERVER_IDENTIFIER=54,
    CLIENT_IDENTIFIER=61,
    TFTP_SERVER_NAME=66
)


REQUEST = utils.make_enum(
    DISCOVER=1,
    OFFER=2,
    REQUEST=3,
    DECLINE=4,
    ACK=5,
    NACK=6,
    RELEASE=7,
    INFROM=8
)
