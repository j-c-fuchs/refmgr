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

from collections import defaultdict

from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser import customization as bibc

from . import conf


def customize_key(record):
    """Customize the BibTeX key."""
    MAX_AUTHORS = 100
    entrytype = record['ENTRYTYPE'].lower()

    key = conf.get('bibtex', f'{entrytype}_key', fallback=None)
    if key is None:
        # don't change the BibTeX key
        return record

    substitutions = defaultdict('')
    substitutions.update(record)

    substitutions['original_key'] = record['ID']

    if ('shortjournal' not in substitutions
            and 'journal' in substitutions):
        substitutions['shortjournal'] = substitutions['journal']
    if ('shortjournal_' not in substitutions
            and 'shortjournal' in substitutions):
        substitutions['shortjournal_'] = (
            substitutions['shortjournal'].replace('.', '')
            )

    # make a copy of record because bibc.author isn't a pure function
    authors = bibc.author(record.copy())['author']
    lastnames = [''.join(s for s in name.split(',')[0].split())
                 for name in authors]
    firstauthor = lastnames[0]
    all_authors = ' '.join(lastnames)
    substitutions['firstauthor'] = firstauthor
    substitutions['author'] = all_authors
    for i in range(1, len(authors)):
        substitutions[f'author_max{i}'] = firstauthor + 'et al'
        substitutions[f'author_max{i}_'] = ' '.join(lastnames[:i]) + 'et al'
    for i in range(len(authors), MAX_AUTHORS):
        substitutions[f'author_max{i}'] = all_authors
        substitutions[f'author_max{i}_'] = all_authors

    new_key = key.format(substitutions)
    # remove whitespace
    key_space = conf.get('bibtex', 'key_space', fallback='')
    new_key = key_space.join(new_key.split())

    record['ID'] = new_key

    return record


def customizations(record):
    """Customize a BibTeX entry."""
    record = customize_key(record)

    _homogenize_latex_encoding = conf.getboolean(
        'bibtex', 'homogenize_latex_encoding', fallback=False)
    _convert_to_unicode = conf.getboolean(
        'bibtex', 'convert_to_unicode', fallback=False)
    if _homogenize_latex_encoding and _convert_to_unicode:
        msg = ('invalid config settings: bibtex.homogenize_latex_encoding and '
               'bibtex.convert_to_unicode cannot be used together')
        raise ValueError(msg)
    elif _homogenize_latex_encoding:
        record = bibc.homogenize_latex_encoding
    elif _convert_to_unicode:
        record = bibc.convert_to_unicode

    return record


def init_parser():
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

    bparser.customization = customizations

    return bparser


def init_writer():
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
