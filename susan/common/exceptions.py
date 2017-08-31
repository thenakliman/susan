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


class SusanException(Exception):
    pass


class NotFoundException(SusanException):
    message = ("Not found")


class ConflictException(SusanException):
    message = ("Conflict occured")


class SubnetNotFoundException(NotFoundException):
    message = ("Subnet id of %(interface)s on %(datapath_id) "
               "could not be found")

class SubnetNotDefinedException(NotFoundException):
    message = ("Subnet %(subnet_id)s is not registered")


class DHCPServerNotFoundException(NotFoundException):
    message = ("DHCP server for %(subnet_id) subnet not found")


class ParameterNotFoundException(NotFoundException):
    message = ("Parameter for %(mac)s on %(port)s port of  %(datapath_id)s not found")


class AlreadyAssignedDiffIPException(ConflictException):
    message = ("Aleardy assigned %(ip)s to %(mac)s in %(subnet_id)s")


class AlreadyAssignedIPException(ConflictException):
    message = ("Aleardy assigned %(ip)s to %(mac)s in %(subnet_id)s")


class MACNotFound(NotFoundException):
    message = ("MAC for %(ip)s in %(subnet_id)s could not be found")


class DHCPNotFound(NotFoundException):
    message = ("DHCP server in %(subnet_id)s subnet could not be found")

class PatameterNotFoundException(NotFoundException):
    message = ("Parameter for %(mac)s in %(subnet_id)s not found")
