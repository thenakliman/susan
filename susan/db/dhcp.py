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

import abc, ABCMeta
import six


@six.add_metaclass(ABCMeta)
class DHCPDB(object):
    def __init__(self):
        pass

    @abstractmethod
    def release_ip(self, ip, subnet_id, mac):
        pass

    @abstractmethod
    def get_ip(self, subnet_id, mac):
        pass

    @abstractmethod
    def commit_ip(self, subnet_id, mac, ip):
        pass

    @abstractmethod
    def get_parameters(subnet_id, mac=None):
        pass

    @abstractmethod
    def reserve_ip(self, ip, subnet_id, mac):
        pass

    @abstractmethod
    def add_subnet(self, network, cidr, gateway=None):
        pass

    @abstractmethod
    def update_subnet(self, id, network=None, cidr=None, gateway=None):
        pass

    @abstractmethod
    def add_range(self, subnet_id, start_ip, end_ip):
        pass

    @abstractmethod
    def add_data(self, subnet_id, mac=None, data=None):
        pass

    @abstractmethod
    def add_reserve_ip(self, ip, mac, subnet_id, state,
                       interface, is_reserved=True, lease_time=None,
                       renew_time=None, expire_time=None):
        pass

    @abstractmethod
    def update_range(self, subnet_id, start_ip=None, end_ip=None):
        pass

    @abstractmethod
    def update_data(self, subnet_id, mac=None, data=None):
        pass

    @abstractmethod
    def update_reserve_ip(self, mac, subnet_id, ip=None,
                          interface=None, is_reserved=True, lease_time=None,
                          renew_time=None, expire_time=None):
        pass

    @abstractmethod
    def delete_subnet(self, id_):
        pass

    @abstractmethod
    def delete_range(self, subnet_id):
        pass

    @abstractmethod
    def delete_data(self, subnet_id, mac):
        pass

    @abstractmethod
    def delete_reserve_ip(self, mac, subnet_id):
        pass
