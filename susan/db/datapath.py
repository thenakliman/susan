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

from abc import ABCMeta
from abc import abstractmethod

import six

@six.add_metaclass(ABCMeta)
class Datapath(object):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def add_datapath(id, host, port):
        pass

    @abstractmethod
    def update_datapath(id, host=None, port=None):
        pass

    @abstractmethod
    def delete_datapath(id):
        pass

    @abstractmethod
    def get_datapath(id):
        pass
