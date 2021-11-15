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


"""CLI interface of refmgr."""

import argparse
import os.path
import sys

from . import __version__, conf
from . import config
from .references import import_refs


def configure(args):
    """Print out the configuration."""
    conf.write(sys.stdout)


def main():
    """Main program.

    Currently, only a short notice is printed.
    """
    default_conf_path = '~/.config/refmgr/conf'

    parser = argparse.ArgumentParser(prog='refmgr')
    parser.add_argument('--version', action='version',
                        version=f'This is %(prog)s, version {__version__}.')
    parser.add_argument('-c', action='store', default=default_conf_path,
                        help=f"config file (default: '{default_conf_path}'")
    subparsers = parser.add_subparsers()

    config_parser = subparsers.add_parser('config')
    config_parser.set_defaults(func=configure)

    import_parser = subparsers.add_parser('import')
    import_parser.set_defaults(func=import_refs)
    import_parser.add_argument('refs', nargs='+')

    # parse the command line arguments
    args = parser.parse_args()

    # parse the config file
    conf_path = os.path.realpath(
        os.path.normpath(
            os.path.expanduser(
                args.c)))
    config.load(conf, conf_path)

    args.func(args)
