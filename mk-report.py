#!/usr/bin/env python

"""
Given a directory of nimrodel json output files,
produce an HTML report
"""


from __future__ import print_function
from collections import defaultdict
from os import path as fp
import argparse
import copy
import itertools
import json
import glob
import os
import xml.etree.cElementTree as ET

# ---------------------------------------------------------------------
# report format
# ---------------------------------------------------------------------

# columns to emit in the report
_PRIMARY_COL = 'origOccurence'
_DEFAULT_COLS = [_PRIMARY_COL,
                 'count',
                 'firstname',
                 'surname',
                 'gender',
                 'title']


def _get_colnames(records):
    """
    Return ordered list of attributes to print out as table columns
    """
    keyset = set(_DEFAULT_COLS)
    for _, record in records.iteritems():
        for subrecord in record:
            keyset.update(subrecord.keys())
    return _DEFAULT_COLS +\
        sorted(keyset - frozenset(_DEFAULT_COLS))


def _fill_header(colnames, htable):
    """
    Add table header row
    """
    hrow = ET.SubElement(htable, 'tr')
    hcol = ET.SubElement(hrow, 'th')
    hcol.text = 'file'
    for col in colnames:
        hcol = ET.SubElement(hrow, 'th')
        hcol.text = col


def _fill_columns(subrecord, colnames, hrow):
    """
    Populate a row with elements from a record
    """
    for colname in colnames:
        hcol = ET.SubElement(hrow, 'td')
        if colname in subrecord:
            hcol.text = unicode(subrecord[colname])


def _add_rowset(filename, record, colnames, htable):
    """
    Add rows to the table, one for each subrecord
    """
    hrow = ET.SubElement(htable, 'tr')
    hcol = ET.SubElement(hrow, 'th')
    hcol.text = filename
    if record:
        _fill_columns(record[0], colnames, hrow)
        for subrec in record[1:]:
            hrow = ET.SubElement(htable, 'tr')
            hcol = ET.SubElement(hrow, 'th')
            _fill_columns(subrec, colnames, hrow)


def _mk_report(records, ofile):
    """
    dictionary of records to html tree
    """
    htree = ET.Element('html')
    hbody = ET.SubElement(htree, 'body')
    htable = ET.SubElement(hbody, 'table')

    colnames = _get_colnames(records)
    _fill_header(colnames, htable)
    for fname in sorted(records):
        _add_rowset(fname, records[fname], colnames, htable)
    ET.ElementTree(htree).write(ofile)

# ---------------------------------------------------------------------
# condensing
# ---------------------------------------------------------------------


def _subrec_key(subrec):
    """
    Hashabel representation of a subrecord
    """
    return tuple(sorted(subrec.items()))


def _condense_helper(subrecs):
    """
    count the instances of a subrecord within a record
    """
    counts = defaultdict(int)
    subrecs2 = []
    for subrec in subrecs:
        key = _subrec_key(subrec)
        if key not in counts:
            subrec2 = copy.copy(subrec)
            subrecs2.append(subrec2)
        counts[key] += 1
    for subrec in subrecs2:
        subrec['count'] = counts[_subrec_key(subrec)]
    return subrecs2


def _condense_records(records):
    """
    remove duplicate subrecords but keep track of the times they occur
    """
    records2 = {}
    for fname, subrecords in records.items():
        records2[fname] = sorted(_condense_helper(subrecords),
                                 key=lambda d: d.get(_PRIMARY_COL))
    return records2


def _supercondense_record(records):
    """
    squash all records into a single dir-wide record

    (returns that one list instead of a dictionary)
    """
    elems = itertools.chain.from_iterable(records.values())
    return sorted(_condense_helper(elems),
                  key=lambda d: d.get(_PRIMARY_COL))

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------


def _read_inputs(inputdir):
    """
    Read input dir, return dictionary from filenames to json records
    """
    records = {}
    for filename in glob.glob(fp.join(inputdir, '*')):
        with open(filename) as ifile:
            bname = fp.basename(filename)
            records[bname] = json.load(ifile)
    return records


def _norm_records(records):
    """
    Tidy up whitespace within records
    """
    records2 = {}
    for fname, subrecs in records.items():
        subrecs2 = []
        for subrec in subrecs:
            subrec2 = {}
            for key in subrec:
                subrec2[key] = " ".join(subrec[key].split())
            subrecs2.append(subrec2)
        records2[fname] = subrecs2
    return records2


def main():
    """
    Read input dir, dump in output dir
    """
    psr = argparse.ArgumentParser(description='TTT converter')
    psr.add_argument('input', metavar='DIR', help='dir with json files')
    psr.add_argument('output', metavar='DIR', help='output directory')
    args = psr.parse_args()
    if not fp.exists(args.output):
        os.makedirs(args.output)
    # just report each json object
    records = _norm_records(_read_inputs(args.input))
    _mk_report(records, fp.join(args.output, "report.html"))
    # squash and sort within each file
    crecords = _condense_records(records)
    _mk_report(crecords, fp.join(args.output, "condensed.html"))
    # squash and sort the whole thing
    bname = fp.basename(args.input)
    drecords = {bname: _supercondense_record(records)}
    _mk_report(drecords, fp.join(args.output, "single.html"))


main()
