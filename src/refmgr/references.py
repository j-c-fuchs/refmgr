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

"""Import references."""

import logging
import os.path
import warnings
import shutil

from bibtexparser.bibdatabase import BibDatabase

from . import conf
from . import bibtex
from . import complete


def library_path():
    """Return the normalized library path."""
    return os.path.realpath(
        os.path.normpath(
            os.path.expanduser(
                conf['library']['path'])))

def import_refs(args):
    """Import the given references."""
    for ref in args.refs:
        import_bib(ref, args.single, args.complete, args.copy, args.rename)


def new_bib_path(path):
    """Make the new path for the BibTeX file."""
    basename = os.path.basename(path)
    dirname = library_path()
    return os.path.join(dirname, basename)


def single_bib_path(entry):
    """Return the path of a BibTeX file with a single entry."""
    print(f'{entry = }, {type(entry) = }')
    basename = entry['ID']
    dirname = library_path()
    return os.path.join(dirname, f'{basename}.bib')


def subs_ext(path, ext):
    """Substitute the extension of `path` with `ext` and return the new
    path."""
    root, _ = os.path.splitext(path)
    ext = ext.rstrip('.')
    return f'{root}.{ext}'


def write_database(db, outpath, overwrite=False):
    """Write the BibDatabase `db` to the path `outpath`."""
    bwriter = bibtex.init_writer()
    mode = 'w' if overwrite else 'x'

    try:
        if os.path.exists(outpath):
            msg = f'overwriting {outpath}'
            logging.info(msg)
        with open(outpath, mode) as outfile:
            msg = f'writing to {outpath}'
            logging.info(msg)
            outfile.write(bwriter.write(db))
    except FileExistsError:
        msg = f"skipping writing to {outpath}: file already exists"
        warnings.warn(msg, RuntimeWarning)


def import_bib(path, single=False, completions=None, copy=None, rename=False):
    """Import the bibtex file at the given path.

    If `single` is `False`, the every import file is saved in the library.
    If it is `True`, a new file will be created for every BibTeX entry
    in the library; it's name will be the BibTeX key with the suffix '.bib'.
    """
    if completions is None:
        completions = []
    if copy is None:
        copy = []

    # convert strings to complete.Completion
    completions = [complete.Completion[c.upper()] for c in completions]

    bparser = bibtex.init_parser()

    with open(path, 'r') as infile:
        db = bparser.parse_file(infile)

    db.entries = [complete.complete(e, completions) for e in db.entries]

    if single:
        db2 = BibDatabase()
        db2.strings = db.strings
        for entry in db.entries:
            db2.entries = [entry]
            outpath = single_bib_path(entry)
            write_database(db2, outpath)
        if copy:
            logging.info('skip copying %s: importing as single files', copy)
    else:
        outpath = new_bib_path(path)
        if rename:
            if len(db.entries) > 1:
                warnings.warn(f'renaming {path} not possible: '
                              'more than one reference found')
            elif db.entries:
                outpath = single_bib_path(db.entries[0])
        write_database(db, outpath)
        for ext in copy:
            try:
                src = subs_ext(path, ext)
                dst = subs_ext(outpath, ext)
                logging.info('copying %s to %s', src, dst)
                shutil.copyfile(src, dst)
            except FileNotFoundError:
                continue
