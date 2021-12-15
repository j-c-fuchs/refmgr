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
import logging
import csv

from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser import customization as bibc
import pkg_resources

from . import conf


class Journals:
    to_abbreviation = {}
    from_abbreviation = {}

    @classmethod
    def load_data(cls):
        """Load the journal abbreviations."""
        logging.debug('loading journal abbreviations')
        path = pkg_resources.resource_filename(
            __name__, 'data/journal_abbreviations.csv')
        with open(path, 'rt') as file:
            data = csv.reader(file, delimiter=';', quoting=csv.QUOTE_NONE)

            from_abbreviation = {}
            to_abbreviation = {}
            for row in data:
                try:
                    journal = row[0].strip()
                    shortjournal = row[1].strip()
                except IndexError:
                    continue

                to_abbreviation[journal] = shortjournal
                from_abbreviation[shortjournal] = journal

        cls.to_abbreviation = to_abbreviation
        cls.from_abbreviation = from_abbreviation

    @classmethod
    def from_record(cls, record):
        """Return the journal name and it's abbreviation of the BibTeX entry
        `record`.

        Returns a tuple `(journal, journal_abbreviation)`.  If the journal is
        not known, `(None, None)` is returned.
        """
        if not (cls.to_abbreviation and cls.from_abbreviation):
            logging.debug('len(%s.to_abbreviation) = %s',
                          cls, len(cls.to_abbreviation))
            logging.debug('len(%s.from_abbreviation) = %s',
                          cls, len(cls.from_abbreviation))
            cls.load_data()

        journal = record.get('journal')
        shortjournal = record.get('shortjournal')
        logging.debug('journal = %s, shortjournal = %s', journal, shortjournal)

        if journal is not None:
            journal, shortjournal = cls.from_journal(journal)
        elif shortjournal is not None:
            journal, shortjournal = cls.from_journal(shortjournal)

        return journal, shortjournal

    @classmethod
    def from_journal(cls, journal):
        """Return the journal name and it's abbreviation from a journal name.

        The input `journal` is typically the journal name or it's abbreviation
        Returns a tuple `(full_name, abbreviation)`.  If the journal is
        unknown, `(None, None)` is returned.  Typically, one of the output
        values is the input `journal`.
        """
        out = None, None

        full = cls.from_abbreviation.get(journal)
        abbrev = cls.to_abbreviation.get(journal)
        logging.debug('full = %s, abbrev = %s', full, abbrev)

        if abbrev is not None:
            out = journal, abbrev
        elif full is not None:
            abbrev = cls.to_abbreviation.get(full, journal)
            out = full, abbrev

        return out


def customize_key(record):
    """Customize the BibTeX key."""
    MAX_AUTHORS = 100
    MAX_TITLE = 100
    entrytype = record['ENTRYTYPE'].lower()

    key = conf.get('bibtex', f'{entrytype}_key', fallback=None)
    if key is None:
        # don't change the BibTeX key
        return record

    substitutions = defaultdict(lambda: '')
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

    # make a copy of record because bibc.author isn't a pure function
    title_words = record['title'].split()
    for i in range(1, len(title_words)):
        substitutions[f'title_max{i}'] = ' '.join(title_words[:i])
    for i in range(len(title_words), MAX_TITLE):
        substitutions[f'title_max{i}'] = ' '.join(title_words)

    new_key = key.format_map(substitutions)
    # remove whitespace
    key_space = conf.get('bibtex', 'key_space', fallback='')
    new_key = key_space.join(new_key.split())

    record['ID'] = new_key

    return record


def customize_journal(record):
    """Change to full length journal title and return the record.

    Tries to substitute the journal title with the full length title and to add
    a shortjoural field with the abbreviation.  If the journal is unknown,
    nothing is done.
    """
    journal, shortjournal = Journals.from_record(record)
    if journal is not None:
        record['journal'] = journal
    if shortjournal is not None:
        record['shortjournal'] = shortjournal
    return record


def customize_abbreviate_journal(record):
    """Change to the abbreviated journal title and return the record.

    Removes the shortjouralfield if it exists.  If the journal or its
    abbreviation is unknown, nothing is done.
    """
    journal, shortjournal = Journals.from_record(record)
    if shortjournal is not None:
        record['journal'] = shortjournal
        record.pop('shortjournal', None)
    return record


def convert_month(record):
    """Convert the month to a number."""
    month_dict = {
        'jan': '1',
        'feb': '2',
        'mar': '3',
        'apr': '4',
        'may': '5',
        'jun': '6',
        'jul': '7',
        'aug': '8',
        'sep': '9',
        'okt': '10',
        'nov': '11',
        'dec': '12',
        'january': '1',
        'february': '2',
        'march': '3',
        'april': '4',
        'june': '6',
        'july': '7',
        'august': '8',
        'september': '9',
        'oktober': '10',
        'november': '11',
        'december': '12',
    }
    month = record.get('month')
    if month is not None:
        month = month_dict.get(month.lower())
        if month is not None:
            record['month'] = month

    return record


def normalize_doi(record):
    """Normalize the DOI and return the record."""
    doi = record.get('doi')
    if doi is not None:
        doi = doi.removeprefix('https://doi.org/')
        doi = doi.removeprefix('http://doi.org/')
        doi = doi.removeprefix('https://dx.doi.org/')
        doi = doi.removeprefix('http://dx.doi.org/')
        record['doi'] = doi

    return record


def remove_empty_fields(record):
    """Remove empty fields and return the record."""
    emtpy_fields = [k for k, v in record.items() if not v]
    for field in emtpy_fields:
        del record[field]
    return record


def customizations(record):
    """Customize a BibTeX entry."""
    if conf.getboolean('bibtex', 'convert_month', fallback=False):
        record = convert_month(record)

    if conf.getboolean('bibtex', 'abbreviate_journals', fallback=False):
        record = customize_abbreviate_journal(record)
    elif conf.getboolean('bibtex', 'normalize_journals', fallback=False):
        record = customize_journal(record)

    if conf.getboolean('bibtex', 'normalize_doi', fallback=False):
        record = normalize_doi(record)

    if conf.getboolean('bibtex', 'remove_empty_fields', fallback=False):
        record = remove_empty_fields(record)

    _homogenize_latex_encoding = conf.getboolean(
        'bibtex', 'homogenize_latex_encoding', fallback=False)
    _convert_to_unicode = conf.getboolean(
        'bibtex', 'convert_to_unicode', fallback=False)
    if _homogenize_latex_encoding and _convert_to_unicode:
        msg = ('invalid config settings: bibtex.homogenize_latex_encoding and '
               'bibtex.convert_to_unicode cannot be used together')
        raise ValueError(msg)
    elif _homogenize_latex_encoding:
        record = bibc.homogenize_latex_encoding(record)
    elif _convert_to_unicode:
        record = bibc.convert_to_unicode(record)

    record = customize_key(record)

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
