#!/usr/bin/env python

"""
Extract natural language requests from SC8 petitions
files.

The files seem to be in some informal? text based
attribute-value pairs

Note that there is interesting metadata in here in the form of
annotated entities. It'd be useful to mine these for some sort
of lexicon
"""

# TODO: extract petitioners, etc fields
# TODO: endorsements


from __future__ import print_function
from os import path as fp
from collections import namedtuple
import argparse
import codecs
import glob
import os
import re


_BLOCK_START = "Reference and Date"
_TEXT_DIR = "text"

_REQ_START = re.compile(r"^((\d\) )?Nature of request:\s*)")
_REQ_END = re.compile(r"^(Endorsement|Other information)")
_REFERENCE = re.compile(r"^Reference:\s*(.*)\s*$")
_DATE = re.compile(r"^Date:\s*\[(.*)\]")

_REF_PARTS = re.compile(r"[ /]")


class Petition(namedtuple("Petition",
                          ["reference",
                           "date",
                           "request",
                           "endorsement"])):
    "A record within an SC8 file"
    pass


def extract_petition(block):
    """
    extract information from a block of lines corresponding
    to one petition

    :: [String] -> Petition
    """

    request_start = False
    request = []
    ref = None
    date = None
    endorsement = None
    for line in block:
        if request_start and _REQ_END.match(line):
            break
        elif request_start:
            request.append(line)
        elif _DATE.match(line):
            date = _DATE.sub(r"\1", line)
        elif _REFERENCE.match(line):
            ref = _REFERENCE.sub(r"\1", line)
        elif _REQ_START.match(line):
            rest = _REQ_START.sub("", line)
            if rest.startswith("["):
                request = None
            else:
                request_start = True
                request = [rest]

    return Petition(reference=ref,
                    date=date,
                    request=request,
                    endorsement=endorsement)


def save_petition(petition, odir):
    """
    write a petition to the output dir

    :: (Petition, FilePath) -> IO ()
    """

    if petition.request is None:
        return

    ref_parts = _REF_PARTS.split(petition.reference)
    ref_subdir = "-".join(ref_parts[:3])
    dname = fp.join(odir, _TEXT_DIR, ref_subdir)
    if not fp.exists(dname):
        os.makedirs(dname)
    filename = fp.join(dname, "-".join(ref_parts))

    lines = []
    if petition.date is not None:
        lines.append(petition.date)
    lines.extend(petition.request)

    with codecs.open(filename, 'w', 'utf-8') as stream:
        print("\n\n".join(lines), file=stream)


def convert(ifile, odir):
    """
    read petitions file; write records
    """
    with codecs.open(ifile, 'r', 'iso8859-1') as stream:
        block = []
        for line in stream.readlines():
            if line.startswith(_BLOCK_START):
                if any(block):  # block has non-empty lines
                    petition = extract_petition(block)
                    save_petition(petition, odir)
                block = []
            block.append(line.strip())


def main():
    """
    Read input dir, dump in output dir
    """
    psr = argparse.ArgumentParser(description='TTT petitions converter')
    psr.add_argument('input', metavar='DIR', help='dir with .dat files')
    psr.add_argument('output', metavar='DIR', help='output directory')
    args = psr.parse_args()
    for ifile in glob.glob(fp.join(args.input, '*.dat')):
        convert(ifile, args.output)

main()
