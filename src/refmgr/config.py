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


def default():
    """Return the default config."""
    conf = configparser.ConfigParser()
    conf['library'] = {'path': '~/Documents/refmgr/'}
    return conf


def config(path='~/.config/refmgr/conf'):
    """Returns the config after reading the config file at `path`."""
    conf = default()

    try:
        with open(path, 'r') as configfile:
            conf.read(configfile)
    except FileNotFoundError:
        # prevent errors if there is no config file
        pass

    return conf
