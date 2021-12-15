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
from . import complete


def show_config(args):
    """Print out the configuration."""
    conf.write(sys.stdout)


def init_config(args):
    """Initialize the config file."""
    config.init(args.c)


def add_config_parser(subparsers):
    """Add the config (sub)parser and return it."""
    config_parser = subparsers.add_parser('config')
    config_parser.set_defaults(func=show_config)
    config_subparsers = config_parser.add_subparsers()

    init_parser = config_subparsers.add_parser('init')
    init_parser.set_defaults(func=init_config)

    return config_parser


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

    config_parser = add_config_parser(subparsers)

    import_parser = subparsers.add_parser('import')
    import_parser.set_defaults(func=import_refs)
    import_parser.add_argument('--single', action='store_true')
    import_parser.add_argument('--rename', action='store_true')
    valid_completions = [c.lower() for c in complete.Completion.__members__]
    import_parser.add_argument('-c', '--complete', action='append',
                               choices=valid_completions)
    import_parser.add_argument('--copy', action='append')
    import_parser.add_argument('refs', nargs='+')

    # parse the command line arguments
    args = parser.parse_args()

    # prevent errors due to missing tilde expansion (e.g. in open)
    args.c = os.path.realpath(
        os.path.normpath(
            os.path.expanduser(
                args.c)))

    # parse the config file
    config.load(conf, args.c)

    args.func(args)
