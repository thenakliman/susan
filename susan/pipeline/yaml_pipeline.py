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
import yaml

import susan
from susan.common import exceptions
from susan.common import yaml_utils
from susan.pipeline import base


LOG = logging.getLogger(__name__)


YAML_PIPELINE_FILE = '/var/lib/susan/pipeline.yaml'


class YAMLPipeline(base.BasePipeline):
    # TODO(thenakliman): Pipeline verification has to be added, which
    # sure at initialiation time that pipeline is correct. Verification
    # inolves multiple things like, table number in increasing order,
    # cycle does not exist, table number can not be greater **254**,
    # required parameters are provided in pipeline definition etc.
    # There can be many more needs to identify and support the same.
    def __init__(self):
        self.pipeline_file_location = susan.CONF.get('yaml_pipeline',
                                                     'location',
                                                     YAML_PIPELINE_FILE)
        # NOTE: Pipeline file can be loaded on demand as well, but that
        # approach makes it necessary for each operation to check if pipeline
        # needs to be loaded therefore loading file at initialization.
        self.pipeline = self.get_pipeline()

    def get_pipeline(self):
        try:
            pipeline = yaml_utils.get_yaml(self.pipeline_file_location)
        except exceptions.InvalidYamlFormat:
            LOG.exception("Invalid file format, %s file has invalid "
                          "yaml syntax")
            raise exceptions.InvalidPipeline()

        return pipeline

    def _get_app_param(self, app, param):
        """Fetch application parameter"""
        return self.pipeline[app][param]

    def _get_app_config(self, app, config):
        """Fetch configuration parameter for the application"""
        return self.pipeline[app]['config'][config]

    def get_table(self, app):
        try:
            # If table number is fetched before fetching pipeline.
            return self._get_app_param(app, 'table')
        except KeyError:
            raise exceptions.AppNotFound(app=app)

    # NOTE, not being used now
    def _get_app_parameter(self, app):
        """Provides app module and app class"""
        try:
            # If table number is fetched before fetching pipeline.
            cls = self._get_app_param(app, 'app')
            return cls.split('.')
        except KeyError:
            raise exceptions.ClassNotFound(app=app)

    def get_app_class(self, app):
        try:
            return self._get_app_param(app, 'app').split('.')[1]
        except IndexError:
            raise exceptions.InvalidClassDefinition(app=app)

    def get_app_module(self, app):
        try:
            return self._get_app_param(app, 'app').split('.')[0]
        except IndexError:
            raise exceptions.InvalidClassDefinition(app=app)
