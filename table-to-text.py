#!/usr/bin/env python

"""
Squash marked up TTT Early Modern data from tabular format to
simple text format with each row treated as a paragraph, and
each cell treated as line. We drop the distinction between
whitespace within the cells and linebreaks, so don't read any
clever semantics into the whitespace.
"""


from __future__ import print_function
from os import path as fp
import argparse
import codecs
import glob
import htmlentitydefs
import itertools
import os
import re
import xml.etree.ElementTree as ET

from ttt.date import read_date

_OTHER_ENTITIES = {'emacr': 275,
                   'utilde': 361}


# lifted from http://effbot.org/zone/re-sub.htm#unescape-html
# and lightly linted
# exceptions for xml entities added and support for a dictionary
# of additional entities to try
def unescape(text, extra=None):
    """
    Removes HTML character references and entities from a text string.

    :param text The HTML (or XML) source text.
    :return The plain text, as a Unicode string, if necessary.
    """
    _xml_predefined = ["quot", "amp", "apos", "lt", "gt"]
    extra = extra or _OTHER_ENTITIES

    def fixup(match):
        "given a matching entity, return corresponding unicode char"
        text = match.group(0)
        ename = text[1:-1]
        if ename in _xml_predefined:
            return text
        elif text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        elif ename in extra:
            return unichr(extra[ename])
        elif ename in htmlentitydefs.name2codepoint:
            return unichr(htmlentitydefs.name2codepoint[ename])
        return text  # leave as is
    return re.sub(r"&#?\w+;", fixup, text)

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------


def _column_to_text(xml):
    """
    string representation of table column - join all text and ignore
    the markup; will have to watch out for unwanted concatenation if
    there are annotations that assume markup implies whitespace
    """
    return "".join(xml.itertext())


def _row_to_text(xml):
    """
    string representation of table row; all columns separated by lines
    """
    columns = itertools.chain(xml.iter('th'), xml.iter('td'))
    return "\n".join(map(_column_to_text, columns))


def _doc_to_text(xml):
    """
    string representation of entire document
    (WARNING: mutates the tree)
    """
    for br_node in xml.iter('br'):
        br_node.text = "\n"
    rows = map(_row_to_text, xml.iter('tr'))
    return "\n\n".join(rows)


def convert(ifile):
    """
    Return a tuple of

    * string representation of the tabular content in the file
    * date string in its header
    """
    # The data is actually iso-8859-1 converted but it
    # contains entities which are defined elsewhere,
    # so without access to the DTD, we manually translate
    # the entities to unicode chars, encode everything
    # as 'utf-8' and then feed it to a forced-utf-8
    # XML parser
    #
    # Is there a cleaner way to do this?
    parser = ET.XMLParser(encoding='utf-8')
    with codecs.open(ifile, 'r', 'iso-8859-1') as fin:
        utext = unescape(fin.read()).encode('utf-8')
        tree = ET.fromstringlist([utext], parser=parser)
        date_nodes = [n.text for n in tree.iter('head')]
        date_str = read_date(date_nodes[0]) if date_nodes else 'unknown'
        return _doc_to_text(tree), date_str


def main():
    """
    Read input dir, dump in output dir
    """
    psr = argparse.ArgumentParser(description='TTT converter')
    psr.add_argument('input', metavar='DIR', help='dir with xml files')
    psr.add_argument('output', metavar='DIR', help='output directory')
    args = psr.parse_args()
    text_dir = fp.join(args.output, "text")
    date_dir = fp.join(args.output, "dates")
    if not fp.exists(text_dir):
        os.makedirs(text_dir)
    if not fp.exists(date_dir):
        os.makedirs(date_dir)
    for ifile in glob.glob(fp.join(args.input, '*.xml')):
        str_content, date_str = convert(ifile)
        bname = fp.basename(ifile)
        tfile = fp.join(text_dir, fp.splitext(bname)[0] + ".txt")
        with codecs.open(tfile, 'w', 'utf-8') as fout:
            print(str_content, file=fout)
        dfile = fp.join(date_dir, fp.splitext(bname)[0] + ".txt")
        with codecs.open(dfile, 'w', 'utf-8') as fout:
            print(date_str, file=fout)


main()
