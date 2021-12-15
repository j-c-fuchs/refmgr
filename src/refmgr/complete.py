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


"""Complete references with online information."""

import enum
import warnings
import logging

import arxiv


class Completion(enum.Enum):
    """Possible completions for a BibTeX entry."""
    #: Add information about the arXiv eprint:
    #: Add *eprint*, *eprinttype* and *eprintclass* fields.
    ARXIV = enum.auto()


def complete(record, completions):
    """Complete the BibTeX reference `record` with the given `completions`
    and return it.

    `completions` needs to be a sequence of `Completion` instances.
    """
    for completion in completions:
        match completion:
            case Completion.ARXIV:
                record = add_arxiv(record)
            case _:
                msg = f'skipping completing {completion}: not implemented'
                warnings.warn(msg)

    return record


def dois_match(doi1, doi2):
    logging.debug('doi1: %s', doi1)
    logging.debug('doi2: %s', doi2)
    if doi1 is None or doi2 is None:
        return False
    if not (doi1 and doi2):
        return False
    return doi1 in doi2 or doi2 in doi1


def add_arxiv(record):
    """Search for arXiv information and add it to the record.

    Returns the modified record.
    """
    if 'doi' not in record:
        msg = ("arxiv completion not possible for {record['ID']}: "
               "no DOI available")
        warnings.warn(msg, RuntimeWarning)
        logging.debug(msg)
        return record

    query=f"all:{record['doi']}"
    search = arxiv.Search(query=query)
    matches = [result for result in search.results()
               if dois_match(result.doi, record['doi'])]
    logging.debug('matches: %s', str(matches))
    if not matches:
        msg = ("arxiv completion not possible for {record['ID']}: "
               "no matching arxiv articles found")
        warnings.warn(msg, RuntimeWarning)
        return record
    if len(matches) > 1:
        msg = ("arxiv completion not possible for {record['ID']}: "
               "more than one matching arxiv articles found")
        warnings.warn(msg, RuntimeWarning)
        return record

    match = matches[0]
    record['eprint'] = match.entry_id
    record['eprintclass'] = match.primary_category
    record['eprinttype'] = 'arxiv'

    return record
