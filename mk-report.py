#!/usr/bin/env python
# vim:fileencoding=utf-8

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
from ttt.score import score_records, SCORE_KEYS
from ttt.torpor import Torpor

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


def _write_html(ofile, htree):
    """
    Write an HTML tree out
    """
    with codecs.open(ofile, 'wb', 'utf-8') as ofile:
        ofile.write(unicode(htree))


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


def _overview_add_toc(hbody, has_before):
    """
    Add a table of contents section to the overview report
    """
    def mk_report_block(rlist, descr, prefix):
        """
        append a bullet point to a list, pointing to
        various subreports
        """
        item = rlist.li
        item.a(descr, href=prefix+".html")
        if has_before:
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
    if has_before:
        scores_li = rlist.li
        scores_li.a('scores', href='scores.html')
        scores_li.span(' (before = reference)')


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

    _overview_add_toc(hbody, records_before is not None)
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

    _write_html(ofile, htree)

# ---------------------------------------------------------------------
# attributes report
# ---------------------------------------------------------------------


def _add_attribute_factoids(hbody, counts_after, counts_before):
    "add an overview to an attributes counts report"

    def _add_factoid_header(thead):
        """
        Optional before vs. after header for the factoid table
        """
        if counts_before is not None:
            cols = ['', 'before', 'after']
            _add_row(thead, cols, [])

    def _add_factoid(table, description, fun):
        """
        Append a factoid to the table

        :: (Html, String, String -> Int) -> IO ()
        """
        cols = []
        if counts_before is not None:
            cols = [str(fun(counts_before)),
                    str(fun(counts_after))]
        else:
            cols = [str(fun(counts_after))]
        _add_row(table, [description], cols)

    hfactoids = _add_report_table(hbody, fill_head=_add_factoid_header)
    _add_factoid(hfactoids, 'total instances', lambda c: sum(c.values()))
    _add_factoid(hfactoids, 'unique values', lambda c: len(c.keys()))
    _add_factoid(hfactoids, 'singletons',
                 lambda c: len([k for k, v in c.items() if v == 1]))


def _add_attribute_counts(hbody, counts_after, counts_before):
    """
    add the actual counts (the meatist bit) to the attributes
    counts table
    """

    def _add_header(thead):
        "add a header to a count table"
        if counts_before is None:
            cols = [u'value', u'count']
        else:
            cols = [u'value', u'count before', u'count after']
        _add_row(thead, cols, [])

    hcounts = _add_report_table(hbody, fill_head=_add_header)

    keys = sorted(frozenset(counts_after.keys()) |
                  frozenset(counts_before.keys()),
                  key=lambda x: counts_after.get(x, 0),
                  reverse=True)
    for key in keys:
        cols = [key]
        if counts_before is not None:
            cols.append(unicode(counts_before.get(key, 0)))
        cols.append(unicode(counts_after.get(key, 0)))
        _add_row(hcounts, [], cols)


def mk_attribute_subreport(oprefix,
                           all_attrs,
                           attribute,
                           counts_after,
                           counts_before=None):
    """
    Write a table showing the number of items each value for an
    attribute occurs ::

        (FilePath, [String], String, Counter String) -> IO ()

    (the `all_attrs` is used for navigation; it lets us build
    links to the other attributes)
    """
    def _mk_fname(attr):
        "filename for an attribute report"
        return "{}-{}.html".format(oprefix, attr)


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


    hbody.h2(u'overview of ' + attribute)
    _add_attribute_factoids(hbody, counts_after, counts_before)

    hbody.h2(u'values for ' + attribute)
    _add_attribute_counts(hbody, counts_after, counts_before)

    _write_html(_mk_fname(attribute), htree)


def mk_attribute_reports(oprefix, records,
                         records_before=None):
    """
    Write out reports for all reportable attributes.

    Return a list of attributes covered (for future navigation) ::

        (FilePath, Records, Records) -> IO [String]
    """
    censored = [u'origOccurence', u'count', u'article'] + _OPTIONAL_COLS
    colnames = [x for x in _get_colnames(records, records_before)
                if x not in censored]

    def count(recs):
        """
        Counts for a given record set ::

            Records -> Dict String (Counter String)
        """
        # force instantiate (instead of just using defaultdict)
        # because we want to ensure we have a counter even if
        # the key is not present (before/after may have diff attrs)
        counts = {}
        for key in colnames:
            counts[key] = Counter()
        for srec in chain.from_iterable(recs.values()):
            for key, val in srec.items():
                if key in colnames:
                    counts[key][val] += 1
        return counts

    counts_after = count(records)
    if records_before is None:
        counts_before = {k:None for k in colnames}
    else:
        counts_before = count(records_before)

    for attr in colnames:
        mk_attribute_subreport(oprefix, colnames, attr,
                               counts_after[attr],
                               counts_before[attr])

    return colnames


# ---------------------------------------------------------------------
# scoring report
# ---------------------------------------------------------------------


def _save_scores(ofile, agg_scores, indiv_scores, keys):
    """
    Actually generate the scoring table given the computed scores
    """
    htree = XHTML()
    hhead = htree.head
    _add_includes(hhead)
    hhead.meta.style(_REPORT_CSS)

    def _fmt_score(score):
        "Float -> String"
        if score is None:
            return u'0 (N/A)'
        else:
            return u'{:.4}'.format(100. * score)

    def _add_header(thead):
        "add a header to a count table"
        _add_row(thead, ['file'] + SCORE_KEYS, [])

    def _flat_scores(scores):
        "scores as list of columns"
        return [_fmt_score(scores[x]) for x in SCORE_KEYS]

    hbody = htree.body
    hbody.h2(u'aggregate scores')
    h_aggr = _add_report_table(hbody, fill_head=_add_header)
    _add_row(h_aggr, [''], _flat_scores(agg_scores))

    hbody.h2(u'individual scores')
    h_indiv = _add_report_table(hbody, fill_head=_add_header)
    for key in keys:
        _add_row(h_indiv, [key],
                 _flat_scores(indiv_scores[key]))

    _write_html(ofile, htree)


def mk_score_report(ofile, records_ref, records_tst):
    """
    Emit a scoring table, showing precision, recall, etc scores
    for each file as well as an aggregrate score
    """
    with Torpor('computing scores'):
        agg_scores, indiv_scores = \
            score_records(records_ref, records_tst)
    with Torpor('saving scores'):
        _save_scores(ofile, agg_scores, indiv_scores, records_ref.keys())

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
    _write_html(ofile, htree)


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
    with Torpor('reading "after" records [{}]'.format(args.input)):
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
        with Torpor('reading "before" records [{}]'.format(args.before)):
            records_before = _norm_records(read_records(args.before))
        crecords_before = _condense_records(records_before)
        drecords_before = {fp.basename(args.before):
                           _supercondense_record(records_before)}
        with Torpor('making before/after per-file reports'):
            mk_report(rpath("report-before"), records_before)
            mk_report(rpath("report-after"), records)
            mk_report(rpath("condensed-before"), crecords_before)
            mk_report(rpath("condensed-after"), crecords)
        with Torpor('making before/after whole-dir reports'):
            mk_report(rpath("single-before"), drecords_before)
            mk_report(rpath("single-after"), drecords)
        mk_score_report(rpath("scores"), records_before, records)

    else:
        records_before = None
        crecords_before = None
        drecords_before = None

    with Torpor('making attribute reports'):
        mk_attribute_reports(fp.join(args.output, "attr"),
                             drecords,
                             records_before=drecords_before)
    with Torpor('making comparative per-file reports'):
        mk_report(rpath("report"),
                  records,
                  records_before=records_before)
        mk_report(rpath("condensed"),
                  crecords,
                  records_before=crecords_before)
    with Torpor('making comparative whole-dir reports'):
        mk_report(rpath("single"),
                  drecords,
                  records_before=drecords_before)
    mk_overview(rpath("index"),
                records,
                records_before=records_before)


if __name__ == '__main__':
    main()
