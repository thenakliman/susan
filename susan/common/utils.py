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

import netaddr
import struct

from ryu.lib import addrconv


def ipv4_text_to_int(ip_text):
    return struct.unpack('!I', addrconv.ipv4.text_to_bin(ip_text))[0]


def get_packed_address(address):
    """Returns packet ip address."""

    return netaddr.IPAddress(address).packed


def make_type(name, base, **attributes):
    return type(name, base, attributes)


def make_enum(**attributes):
    return make_type('Enum', (), **attributes)
