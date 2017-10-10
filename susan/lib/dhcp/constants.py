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
    # Vendor Extensions
    NETMASK=1,
    ROUTER=3,
    TIME_SERVER=4,
    NAME_SERVER=5,
    DNS_SERVER=6,
    LOG_SERVER=7,
    HOST_NAME=12,
    BOOT_FILE=13,
    DOMAIN_NAME=15,
    END=255,

    # IP Layer parameter per port
    MTU=26,
    BROADCAST_ADDR=28,

    # DHCP EXTENSIONS
    REQUESTED_IP=50,
    LEASE_TIME=51,
    MESSAGE_TYPE=53,
    SERVER_IDENTIFIER=54,
    PARAMETER_REQUEST=55,
    MESSAGE=56,
    MAX_DHCP_SIZE=57,
    RENEWEL_TIME=58,
    REBINDING_TIME=59,
    CLIENT_IDENTIFIER=61,
    TFTP_SERVER_NAME=66,
    BOOT_FILE_NAME=67
)


REQUEST = utils.make_enum(
    DISCOVER=1,
    OFFER=2,
    REQUEST=3,
    DECLINE=4,
    ACK=5,
    NACK=6,
    RELEASE=7,
    INFORM=8
)

DEFAULT_LEASE_TIME = 3600
