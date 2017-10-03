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
import ConfigParser
import logging
import sys

from susan import CONF

import susan
from susan.apps import manager
from susan import version


LOG = logging.getLogger(__name__)

CONFIG_FILE = '/etc/susan/susan.conf'
LOG_FILE = '/var/log/susan'

# TODO(thenakliman): Find some better way to set it.
SERVICE_NAME = 'susan'

def setup_config():
    # TODO(thenakliman): use argparse python module for better
    # parsing of command line arguments
    args = sys.argv
    config_file = CONFIG_FILE

    if len(args) > 2 and args[2] == '--config-file':
        config_file = args[2]

    config = ConfigParser.SafeConfigParser()
    config.read(config_file)
    susan.CONF = config


def setup_logging():
    try:
        # TODO(thenakliman): Find to assign default value for config parser
        log_level = susan.CONF.get('default', 'log_level')
    except ConfigParser.NoSectionError:
        log_level = 'warn'

    formatter = ("%(asctime)s %(levelname)s %(name)s %(funcName)s():%(lineno)s"
                 " PID:%(process)d %(message)s")
    try:
        log_dir = susan.CONF.get('default', 'log_dir')
    except ConfigParser.NoSectionError:
        log_dir = LOG_FILE

    file_name = ("%s/%s.log" % (log_dir, SERVICE_NAME))
    logging.basicConfig(filename=file_name,
                        level=getattr(logging, log_level.upper()),
                        format=formatter)

    # TODO(thenakliman): choose 80 value dynamically, don't hardcode
    LOG.info("*" * 80)
    LOG.info("Logging Enabled !!!!!")
    LOG.info("%(prog)s version %(version)s",
             {'prog': sys.argv[0],
              'version': version.CURRENT_VERSION})
    LOG.debug("command line: %s", " ".join(sys.argv))


def main():
    setup_config()
    setup_logging()
    app_manager.AppManager.run_apps(
        ['susan.apps.manager'])


if __name__ == '__main__':
    main()
