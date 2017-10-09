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


# Their are more than 70 options currently, two category of options are
# important therefore included, more options can be included as per
# requirement

import copy
import struct

from susan.lib.dhcp import constants as const
from susan.common import utils


def struct_pack(value, **kwargs):
    frmt = kwargs.get('format', '!%ss' % max(len(value), 2))
    return struct.pack(frmt, value)


def pack_list_address(values, **kwargs):
    packed_ips = []
    for value in values:
        packed_ips.append(pack_ip(value))

    return packed_ips


def pack_ip(value, **kwargs):
    return utils.get_packed_address(value)

pack_list_address = pack_ip


pack_data = {
    # Vendor Extensions
    const.OPTIONS.NETMASK: {'method': pack_ip},
    const.OPTIONS.ROUTER: {'method': pack_list_address},
    const.OPTIONS.TIME_SERVER: {'method': pack_list_address},
    const.OPTIONS.NAME_SERVER: {'method': pack_list_address},
    const.OPTIONS.DNS_SERVER: {'method': pack_list_address},
    const.OPTIONS.LOG_SERVER: {'method': pack_list_address},
    const.OPTIONS.HOST_NAME: {},
    const.OPTIONS.BOOT_FILE: {'format': '!i'},
    const.OPTIONS.DOMAIN_NAME: {},

    # IP Layer parameter per port
    const.OPTIONS.MTU: {'format': '!H'},
    const.OPTIONS.BROADCAST_ADDR: {'method': pack_ip},

    # DHCP EXTENSIONS
    const.OPTIONS.REQUESTED_IP: {'method': pack_ip},
    const.OPTIONS.LEASE_TIME: {'format': '!L'},
    const.OPTIONS.MESSAGE_TYPE: {'format': '!B'},
    const.OPTIONS.SERVER_IDENTIFIER: {'method': pack_ip},
    # Should not be filled by server
    const.OPTIONS.PARAMETER_REQUEST: {},
    const.OPTIONS.MESSAGE: {},
    const.OPTIONS.MAX_DHCP_SIZE: {'format': '!H'},
    const.OPTIONS.RENEWEL_TIME: {'format': '!I'},
    const.OPTIONS.REBINDING_TIME: {'format': '!I'},
    const.OPTIONS.CLIENT_IDENTIFIER: {'min_len': 2},
    const.OPTIONS.TFTP_SERVER_NAME: {},
    const.OPTIONS.BOOT_FILE_NAME: {}
}


def pack(option, value):
    try:
        pack_info = copy.deepcopy(pack_data[option])
    except KeyError:
        return

    method = pack_info.get('method', struct_pack)
    return method(value, **pack_info)
