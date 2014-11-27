#!/usr/bin/env python

"""
Given a directory of nimrodel json output files,
produce an HTML report
"""

# it's hard to avoid this given the html reports we're handwriting
# pylint: disable=too-many-locals

# pylint: disable=invalid-name
# this is a script, not a module; we don't care about
# its name being invalid
# pylint: enable=invalid-name

from __future__ import print_function
from collections import defaultdict, Counter
from itertools import chain
from os import path as fp
import argparse
import codecs
import copy
import itertools
import glob
import os
import shutil

from html import XHTML

from ttt.cli import read_records

# ---------------------------------------------------------------------
# report format
# ---------------------------------------------------------------------

# columns to emit in the report
_PRIMARY_COL = u'origOccurrence'
_DATE_COL = u'appearanceDate'
_DATE_COL_MIN = u'appearanceDate (min)'
_DATE_COL_MAX = u'appearanceDate (max)'


_DEFAULT_COLS = [_PRIMARY_COL,
                 u'count',
                 u'forename',
                 u'surname',
                 u'article',
                 u'title',
                 u'role',
                 u'provenance']

_OPTIONAL_COLS = [_DATE_COL,
                  _DATE_COL_MIN,
                  _DATE_COL_MAX]


# ---------------------------------------------------------------------
# css and scripts
# ---------------------------------------------------------------------


_REPORT_CSS = """
.navtable {
    border-collapse: collapse;
}

.navtable td {
    padding: 2px;
    border-left: dotted 1px;
    border-right: dotted 1px;
    border-top: invisible;
    border-bottom: invisible;
}
"""

_SORTER_SCRIPT = """
$(document).ready(function()
    {
        $(".report_table").tablesorter();
    }
);
"""

_BEFORE_STYLE = {'style': 'color:grey;'}

# ---------------------------------------------------------------------
# html helpers
# ---------------------------------------------------------------------


def _add_report_table(hbody, fill_head=None):
    """
    Add a sortable report table; return its body

    If you supply a fill_head function, it will be
    used to populate the table's thead element with
    headers
    """
    table = hbody.table(klass="tablesorter report_table")
    if fill_head is not None:
        fill_head(table.thead)
    return table.tbody


def _add_column(hrow, is_header, content):
    """
    Add a column to a row

    Content can either be just a string, or a tuple
    of string and HTML attributes
    """
    if isinstance(content, tuple):
        text, attrs = content
    else:
        text = content
        attrs = {}

# pylint: disable=star-args
    if is_header:
        hrow.th(text, **attrs)
    else:
        hrow.td(text, **attrs)
# pylint: enable=star-args


def _add_row(table, headers, columns):
    """
    Add a row to an html table with a th cell for each
    header and a td cell for each column.

    The headers and columns could optionally be just
    a string, or a tuple of string and attributes

    Returns the row (which you could just ignore as this
    mutates the table)
    """
    hrow = table.tr()
    for col in headers:
        _add_column(hrow, True, col)
    for col in columns:
        _add_column(hrow, False, col)
    return hrow

# ---------------------------------------------------------------------
# overview
# ---------------------------------------------------------------------


def _add_includes(hhead):
    """
    Add javascript/css includes to the report
    """
    for scriptfile in glob.glob('js/*.js'):
        hhead.script(type="text/javascript",
                     src=unicode(scriptfile))
    for stylefile in glob.glob('css/*.css'):
        hhead.link(rel="stylesheet", type="text/css",
                   href=unicode(stylefile))
    hhead.script(_SORTER_SCRIPT)


def count(fun, items):
    """
    (v -> int, [v]) -> int
    """
    return sum(map(fun, items))


def count_and_mean(fun, items):
    """
    ((v -> int), [v]) -> (int, int)
    """
    total = count(fun, items)
    avg = float(total)/len(items) if items else 0.0
    return (total, avg)


def get_num_attrs(items):
    "number of non-empty values for a list of dictionaries"
    non_empty = lambda d: len([v for v in d.values() if v])
    return count(non_empty, items)


def get_num_instances(attr):
    """
    number of times an attribute is non empty ::

        String -> [Dict String a] -> Int
    """
    def inner(items):
        "[Dict String a] -> Int"
        non_empty = lambda d: 1 if d.get(attr) else 0
        return count(non_empty, items)
    return inner


def mk_overview(ofile, records,
                records_before=None):
    """
    Create an HTML report showing some useful numbers about
    our data
    """

    odir = fp.dirname(ofile)

    htree = XHTML()
    hhead = htree.head
    _add_includes(hhead)
    hhead.meta.style(_REPORT_CSS)
    hbody = htree.body

    def _add_header(thead):
        "add a header to a count table"
        cols = ['']
        if records_before is not None:
            cols.append('before total')
            cols.append('after total')
            cols.append('before mean')
            cols.append('after mean')
        else:
            cols.append('total')
            cols.append('mean')
        _add_row(thead, cols, [])

    def _add_stat(table, name, get_stat):
        "add a statistic to a count table"
        cols = []
        hrow = table.tr()

        # link to the attribute report if we have one
        fname = "attr-" + name + ".html"
        if fp.exists(fp.join(odir, fname)):
            hrow.td.a(name, href=fname)
        else:
            cols.append(name)

        sum_aft, avg_aft = count_and_mean(get_stat,
                                          records.values())
        if records_before is not None:
            sum_bef, avg_bef = count_and_mean(get_stat,
                                              records_before.values())
            cols.append(unicode(sum_bef))
            cols.append(unicode(sum_aft))
            cols.append("{:.4}".format(avg_bef))
            cols.append("{:.4}".format(avg_aft))
        else:
            cols.append(unicode(sum_aft))
            cols.append("{:.4}".format(avg_aft))

        for col in cols:
            _add_column(hrow, False, col)

    def mk_report_block(rlist, descr, prefix):
        """
        append a bullet point to a list, pointing to
        various subreports
        """
        item = rlist.li
        item.a(descr, href=prefix+".html")
        if records_before:
            item.span(" (")
            item.a("before", href=prefix+"-before.html")
            item.span(" | ")
            item.a("after", href=prefix+"-after.html")
            item.span(")")

    hbody.h2("reports")
    rlist = hbody.ul
    mk_report_block(rlist, "item by item", "report")
    mk_report_block(rlist, "each file condensed", "condensed")
    mk_report_block(rlist, "whole dir condensed", "single")

    hbody.h2('general counts')
    htotals = _add_report_table(hbody, fill_head=_add_header)
    _add_stat(htotals, 'files', lambda _: 1)
    _add_stat(htotals, 'records', len)
    _add_stat(htotals, 'attributes', get_num_attrs)

    hbody.h2('attributes')
    hattrs = _add_report_table(hbody, fill_head=_add_header)
    attrs = _get_colnames(records, records_before=records_before,
                          default=[])
    for attr in attrs:
        _add_stat(hattrs, attr, get_num_instances(attr))

    with codecs.open(ofile, 'w', 'utf-8') as ofile:
        print(htree, file=ofile)

# ---------------------------------------------------------------------
# attributes report
# ---------------------------------------------------------------------


def mk_attribute_subreport(oprefix,
                           all_attrs,
                           attribute,
                           counts):
    """
    Write a table showing the number of items each value for an
    attribute occurs ::

        (FilePath, [String], String, Counter String) -> IO ()

    (the `all_attrs` is used for navigation; it lets us build
    links to the other attributes)
    """
    def _add_header(thead):
        "add a header to a count table"
        cols = [u'value', u'count']
        _add_row(thead, cols, [])

    def _mk_fname(attr):
        "filename for an attribute report"
        return "{}-{}.html".format(oprefix, attr)

    singletons = [k for k, v in counts.items() if v == 1]

    htree = XHTML()
    hhead = htree.head
    _add_includes(hhead)
    hhead.meta.style(_REPORT_CSS)

    hbody = htree.body
    hbody.h2(u'see also')

    hnav = hbody.table(klass='navtable')
    hnav_tr = hnav.tr
    hnav_tr.td.a('overview', href='index.html')
    hnav_tr.td()
    for attr in all_attrs:
        if attr == attribute:
            hnav_tr.td.span(attr)
        else:
            hnav_tr.td.a(attr,
                         href=fp.basename(_mk_fname(attr)))

    hbody.h2(u'values for ' + attribute)

    hfactoids = hbody.ul
    hfactoids.li(u'total values: {}'.format(sum(counts.values())))
    hfactoids.li(u'unique values: {}'.format(len(counts.keys())))
    hfactoids.li(u'singletons: {}'.format(len(singletons)))

    hcounts = _add_report_table(hbody, fill_head=_add_header)

    for value, num in sorted(counts.items(),
                             key=lambda x: x[1], reverse=True):
        _add_row(hcounts, [], [value, str(num)])

    with codecs.open(_mk_fname(attribute), 'w', 'utf-8') as stream:
        # not sure why I have to explicitly render the tree as
        # unicode here and not elsewhere
        print(unicode(htree), file=stream)


def mk_attribute_reports(oprefix, records,
                         records_before=None):
    """
    Write out reports for all reportable attributes.

    Return a list of attributes covered (for future navigation) ::

        (FilePath, Records, Records) -> IO [String]
    """
    censored = [u'origOccurrence', u'count', u'article'] + _OPTIONAL_COLS
    colnames = [x for x in _get_colnames(records, records_before)
                if x not in censored]
    counts = defaultdict(Counter)
    for srec in chain.from_iterable(records.values()):
        for key, val in srec.items():
            if key in colnames:
                counts[key][val] += 1

    for attr in colnames:
        mk_attribute_subreport(oprefix, colnames, attr, counts[attr])

    return colnames


# ---------------------------------------------------------------------
# tabular report
# ---------------------------------------------------------------------


def _get_colnames(records, records_before=None,
                  default=None):
    """
    Return ordered list of attributes to print out as table columns
    """
    default = _DEFAULT_COLS if default is None else default
    keyset = set(default)
    records_before = records_before or {}
    for _, record in itertools.chain(records.iteritems(),
                                     records_before.iteritems()):
        for subrecord in record:
            keyset.update(subrecord.keys())

    optional = [x for x in _OPTIONAL_COLS if x in keyset]
    remainder = sorted(keyset - frozenset(default) - frozenset(optional))
    return default + optional + remainder


def _add_report_row(colnames, htable, subrecord,
                    filename=None,
                    is_before=False):
    """
    Populate a row with elements from a record
    """
    if is_before:
        mk_content = lambda t: (t, _BEFORE_STYLE)
    else:
        mk_content = lambda t: t

    headers = [filename or ""]
    columns = [mk_content(unicode(subrecord.get(c, "")))
               for c in colnames]
    _add_row(htable, headers, columns)


def _add_rowset(filename, colnames, htable, record,
                record_before=None):
    """
    Add rows to the table, one for each subrecord
    """
    record_after = record
    if record_before:
        _add_report_row(colnames, htable, record_before[0],
                        filename=filename,
                        is_before=True)
        for subrec in record_before[1:]:
            _add_report_row(colnames, htable, subrec,
                            is_before=True)
    elif record:
        _add_report_row(colnames, htable, record[0],
                        filename=filename)
        record_after = record[1:]

    for subrec in record_after:
        _add_report_row(colnames, htable, subrec)


def mk_report(ofile, records,
              records_before=None):
    """
    dictionary of records to html tree
    """
    htree = XHTML()
    _add_includes(htree)

    colnames = _get_colnames(records, records_before)
    mkcols = lambda h: _add_row(h, ['file'] + colnames, [])
    htable = _add_report_table(htree.body,
                               fill_head=mkcols)

    fnames = set(records.keys())
    fnames = fnames | set(records_before.keys() if records_before else [])
    for fname in sorted(fnames):
        record_before = None if records_before is None\
            else records_before.get(fname)
        record_after = records.get(fname, [])
        _add_rowset(fname, colnames, htable, record_after,
                    record_before=record_before)
    with open(ofile, 'wb') as ofile:
        ofile.write(unicode(htree).encode('utf-8'))


def _copy_includes(odir):
    "copy the javascript/css files to output dir"

    for src in ['js', 'css']:
        dst = fp.join(odir, src)
        if not fp.exists(dst):
            shutil.copytree(src, dst)


# ---------------------------------------------------------------------
# condensing
# ---------------------------------------------------------------------


def _subrec_key(subrec):
    """
    Hashable representation of a subrecord
    """
    def tweak(pair):
        "adjust key values pairs"
        key = pair[0]
        return (key, "-") if key == _DATE_COL else pair

    return tuple(sorted(map(tweak, subrec.items())))


def _condense_helper(subrecs):
    """
    count the instances of a subrecord within a record
    """
    counts = defaultdict(int)
    dates = defaultdict(set)
    subrecs2 = []
    for subrec in subrecs:
        key = _subrec_key(subrec)
        if key not in counts:
            subrec2 = copy.copy(subrec)
            subrecs2.append(subrec2)
        counts[key] += 1
        date = subrec2.get(_DATE_COL)
        if date is not None:
            dates[key].add(date)

    has_date_range = any(dates.values())

    for subrec in subrecs2:
        key = _subrec_key(subrec)
        subrec['count'] = counts[key]
        sdates = dates.get(key)
        if sdates is None:
            pass
        elif not has_date_range:
            subrec[_DATE_COL] = list(sdates)[0]
        else:
            subrec[_DATE_COL_MIN] = min(sdates)
            subrec[_DATE_COL_MAX] = max(sdates)
            if _DATE_COL in subrec:
                del subrec[_DATE_COL]
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
    psr.add_argument('--before', metavar='DIR',
                     help='another dir with json files (for comparsion)')
    args = psr.parse_args()
    if not fp.exists(args.output):
        os.makedirs(args.output)

    # straightforward one row per json object
    records = _norm_records(read_records(args.input))
    # squashed and sorted within each file
    crecords = _condense_records(records)
    # squashed and sorted altogether
    drecords = {fp.basename(args.input):
                _supercondense_record(records)}

    _copy_includes(args.output)

    rpath = lambda f: fp.join(args.output, f + ".html")

    # if we're in diff mode
    if args.before:
        records_before = _norm_records(read_records(args.before))
        crecords_before = _condense_records(records_before)
        drecords_before = {fp.basename(args.before):
                           _supercondense_record(records_before)}
        mk_report(rpath("report-before"), records_before)
        mk_report(rpath("report-after"), records)
        mk_report(rpath("condensed-before"), crecords_before)
        mk_report(rpath("condensed-after"), crecords)
        mk_report(rpath("single-before"), drecords_before)
        mk_report(rpath("single-after"), drecords)
    else:
        records_before = None
        crecords_before = None
        drecords_before = None

    mk_attribute_reports(fp.join(args.output, "attr"),
                         drecords,
                         records_before=drecords_before)
    mk_overview(rpath("index"),
                records,
                records_before=records_before)
    mk_report(rpath("report"),
              records,
              records_before=records_before)
    mk_report(rpath("condensed"),
              crecords,
              records_before=crecords_before)
    mk_report(rpath("single"),
              drecords,
              records_before=drecords_before)


if __name__ == '__main__':
    main()
