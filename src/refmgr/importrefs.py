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

from . import conf
from . import bibtex


def import_refs(args):
    """Import the given references."""
    for ref in args.refs:
        import_bib(ref)


def new_bib_path(path):
    """Make the new path for the BibTeX file."""
    basename = os.path.basename(path)
    dirname = os.path.realpath(
        os.path.normpath(
            os.path.expanduser(
                conf['library']['path'])))
    return os.path.join(dirname, basename)


def write_database(db, path, outpath):
    """Write the BibDatabase `bib` to the path `outpath`."""
    bwriter = bibtex.init_writer()

    try:
        with open(outpath, 'x') as outfile:
            outfile.write(bwriter.write(db))
            msg = f"imported '{path}' to '{outpath}'"
            logging.info(msg)
    except FileExistsError:
        msg = f"cannot import '{path}': '{outpath}' already exists"
        warnings.warn(msg, RuntimeWarning)


def import_bib(path):
    """Import the bibtex file at the given path."""
    bparser = bibtex.init_parser()

    with open(path, 'r') as infile:
        db = bparser.parse_file(infile)

    outpath = new_bib_path(path)
    write_database(db, path, outpath)
