# This file is part of refmgr.
# Copyright (C) 2021  Jacob Fuchs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Config of refmgr."""

import configparser
import logging
import shutil

import pkg_resources


def init(path):
    """Initialize a config file at `path`."""
    logging.debug(f"trying to read sample config file")
    sample_conf = pkg_resources.resource_stream(__name__, 'data/sample.conf')
    logging.debug(f"trying to initialize config file '{path}'")
    with open(path, 'xb') as outfile:
        shutil.copyfileobj(sample_conf, outfile)
        logging.debug(f"config file '{path}' succesfully initialized")


def default():
    """Return the default config."""
    conf = configparser.ConfigParser()
    conf['library'] = {'path': '~/Documents/refmgr/'}
    conf['bibtex'] = {'num_indent': '2'}
    conf['bibtex'] = {'key_space': '_'}
    return conf


def load(conf, path):
    """Read the config from `path` into the config `conf`."""
    try:
        logging.debug(f"trying to read config file '{path}'")
        conf.read(path)
        logging.debug(f"config file '{path}' succesfully read")
    except FileNotFoundError:
        # prevent errors if there is no config file
        logging.debug(f"config file at '{path}' not found")
        pass
