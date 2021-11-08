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
import sys

from . import __version__, conf


def configure(args):
    """Print out the configuration."""
    conf.write(sys.stdout)


def main():
    """Main program.

    Currently, only a short notice is printed.
    """
    parser = argparse.ArgumentParser(prog='refmgr')
    parser.add_argument('--version', action='version',
                        version=f'This is %(prog)s, version {__version__}.')
    subparsers = parser.add_subparsers()

    config_parser = subparsers.add_parser('config')
    config_parser.set_defaults(func=configure)

    args = parser.parse_args()
    args.func(args)
