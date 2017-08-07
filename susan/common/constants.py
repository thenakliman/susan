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

from susan.common import utils

# =============================================
# Common Constants
# =============================================
ZERO_IPADDR = '0.0.0.0'
BROADCAST_IP = '255.255.255.255'
BROADCAST_MAC = 'ff:ff:ff:ff:ff:ff'

# =============================================

TABLE = utils.make_enum(
    DEFAULT=0,
    DHCP=10
)


PROTOCOL = utils.make_enum(
    UDP=17,
    TCP=6
)


ETHERTYPE = utils.make_enum(
    IPV4=0x0800,
    ARP=0x0806
)
