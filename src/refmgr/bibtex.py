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

"""Handling bibtex files."""

from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter

from . import conf


def initparser():
    """Initialize and return a new BibTexParser."""
    bparser = BibTexParser()

    if 'common_strings' in conf['bibtex']:
        bparser.common_strings = conf.getboolean(
            'bibtex', 'common_strings')
    if 'homogenize_fields' in conf['bibtex']:
        bparser.homogenize_fields = conf.getboolean(
            'bibtex', 'homogenize_fields')
    if 'ignore_nonstandard_types' in conf['bibtex']:
        bparser.ignore_nonstandard_types = conf.getboolean(
            'bibtex', 'ignore_nonstandard_types')
    if 'interpolate_bibtex_strings' in conf['bibtex']:
        bparser.interpolate_bibtex_strings = conf.getboolean(
            'bibtex', 'interpolate_bibtex_strings')

    return bparser


def initwriter():
    """Initialize and return a new BibTexWriter."""
    bwriter = BibTexWriter()
    if 'add_trailing_comma' in conf['bibtex']:
        bwriter.add_trailing_comma = conf.getboolean(
            'bibtex', 'add_trailing_comma')
    if 'comma_first' in conf['bibtex']:
        bwriter.comma_first = conf.getboolean(
            'bibtex', 'comma_first')
    if 'contents' in conf['bibtex']:
        bwriter.contents = conf['bibtex']['contents'].split()
    if 'display_order' in conf['bibtex']:
        bwriter.display_order = conf['bibtex']['display_order'].split()
    if 'num_indent' in conf['bibtex']:
        bwriter.indent = ' ' * conf.getint('bibtex', 'num_indent')
    if 'order_entries_by' in conf['bibtex']:
        bwriter.order_entries_by = conf['bibtex']['order_entries_by'].split()
    if 'write_common_strings' in conf['bibtex']:
        bwriter.common_strings = conf.getboolean(
            'bibtex', 'write_common_strings')

    return bwriter
