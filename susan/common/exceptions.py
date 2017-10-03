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

import logging


LOG = logging.getLogger(__name__)


class SusanException(Exception):
    """Base Susan Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.
    """
    message = ("An unknown exception occurred.")

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if message:
            self.message = message

        try:
            self.message = self.message % kwargs
        except Exception:
            # kwargs doesn't match a variable in the message
            # log the issue and the kwargs
            LOG.exception('Exception in string format operation, '
                          'kwargs: %s', kwargs)

        super(SusanException, self).__init__(self.message)

    def __str__(self):
        if six.PY3:
            return self.message
        return self.message.encode('utf-8')

    def __unicode__(self):
        return self.message


class NotFoundException(SusanException):
    message = ("Not found")


class ConflictException(SusanException):
    message = ("Conflict occured")


class SubnetNotFoundException(NotFoundException):
    message = ("Subnet id of %(port)s on %(datapath_id)s "
               "could not be found")


class SubnetNotDefinedException(NotFoundException):
    message = ("Subnet %(subnet_id)s is not registered")


class DHCPServerNotFoundException(NotFoundException):
    message = ("DHCP server for %(subnet_id)s subnet not found")


class ParameterNotFoundException(NotFoundException):
    message = ("Parameter for %(mac)s on %(port)s port of %(datapath_id)s "
               "not found")


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


class NextServerNotDefinedException(NotFoundException):
    message = ("Next server could not be found for %(subnet_id) subnet")


class NotAvailableException(SusanException):
    message = ("Resource is not available")


class IPNotAvailableException(NotAvailableException):
    message = ("IPs are not available in %(subnet_id) subnet")


class PortDoesNotFoundException(NotFoundException):
    message = ("Port %(port)s in %(datapath_id)s datapath does not exist")


class RangeNotFoundException(NotFoundException):
    message = ("Range not found in %(subnet_id) subnet")


class CommittedIPNotFoundException(NotFoundException):
    message = ("Committed ip for %(mac)s in %(subnet_id)s subnet, "
               "could not be found")


class FileNotFound(NotFoundException):
    message = ("%(location)s file could not be found")


class InvalidFormat(SusanException):
    message = ("Invalid format")


class InvalidYamlFormat(InvalidFormat):
    message = ("Yaml file %(location) has yaml formatting issue")


class InvalidPipeline(SusanException):
    message = ("Invalid pipeline")


class AppNotFound(NotFoundException):
    message = ("%(app)s app is not registered in the pipeline pipeline")


class ClassNotFound(NotFoundException):
    message = ("Class for %(app)s not found")


class InvalidClassDefinition(SusanException):
    message = ("Invalid class for %(app)s app")
