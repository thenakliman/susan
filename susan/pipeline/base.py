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

import abc
import importlib

import six

import susan
from susan import pipeline


BASE_PIPELINE_LOCATION = 'susan.pipeline'

@six.add_metaclass(abc.ABCMeta)
class BasePipeline(object):
    # TODO(thenakliman): Pipeline verification has to be added, which
    # sure at initialiation time that pipeline is correct. Verification
    # inolves multiple things like, table number in increasing order,
    # cycle does not exist, table number can not be greater **254**,
    # required parameters are provided in pipeline definition etc.
    # There can be many more needs to identify and support the same,
    # therefore an interface needs to added for the same. Some thing
    # like **__verify** can be supported
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_pipeline(self):
        pass

    @abc.abstractmethod
    def get_table(self, app):
        pass

    @abc.abstractmethod
    def get_app_class(self, app)
        pass

    @abc.abstractmethod
    def get_app_module(self, app)
        pass

# TODO(thenakliman): Remove this mapping, don't want to spend a lot
# of time on thinking about it. It can be improved by removing these
# unnecessary parameters.
pipelines = {
    'yaml_pipeline': 'YAMLPipeline'
}


def get_pipeline():
    pipeline = susan.CONF.get('default', 'pipeline', 'yaml_pipeline')
    path = "%s.%s" % (BASE_PIPELINE_LOCATION, pipeline)
    try:
        pipeline_module = importlib.import_module(path)
        pipeline_cls = pipelines.get(pipeline)
        return getattr(pipeline_module, pipeline_cls)()
    except AttributeError, ImportError:
        LOG.exception("Unable to load %s pipeline", path)
        # TODO(thenakliman): Somehow, need to exit the application, if
        # exceptions are raised.
        raise exceptions.InvalidPipeline() 
