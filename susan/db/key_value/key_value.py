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


class DHCPKV(object):
    def __init__(self):
        pass

    def __init__(self, *args, **kwargs):
        super(DHCPDB, self).__init__(*args, **kwargs)
        pass

    def release_ip(self, ip, subnet_id, mac):
        pass

    def get_ip(self, datapath, in_port):
        pass

    def commit_ip(self, subnet_id, mac, ip):
        pass

    def reserve_ip(self, ip, subnet_id, mac):
        pass

    def get_dhcp_server_ip(self, subnet_id):
        pass

    def get_mac(self, subnet_id, ip):
        pass

    def get_dhcp_server_info(self, subnet_id):
        pass

    def get_subnet_id(self, datapath, port):
        pass

    def get_parameter(self, subnet_id, mac):
        pass
