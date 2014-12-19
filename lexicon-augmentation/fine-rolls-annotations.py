#!/usr/bin/env python
# pylint: disable=invalid-name
# weird filename ok because not a module
# pylint: enable=invalid-name

"""
Extract text from Henry III fineroll XML files.
The resulting output may be split into a multitude of very
small text snippets with one directory per roll.
"""


from __future__ import print_function
from os import path as fp
import codecs
import collections
import glob
import os
import xml.etree.ElementTree as ET

from ttt.cli import CliConfig, iodir_argparser

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

_TAGS = ['persName', 'placeName']


def main():
    """
    Read input dir, dump in output dir
    """
    cfg = CliConfig(description='Fine Rolls xml to text',
                    input_description='XML files (manually annotated TEI)',
                    glob='roll*.xml')
    psr = iodir_argparser(cfg)
    args = psr.parse_args()
    values = collections.defaultdict(set)
    for ifile in glob.glob(fp.join(args.input, cfg.glob)):
        tree = ET.parse(ifile)
        for tag in _TAGS:
            for node in tree.iter(tag):
                txt = node.text or ''
                txt = ' '.join(txt.split())
                values[tag].add(txt)
    if not fp.exists(args.output):
        os.makedirs(args.output)
    for key, vals in values.items():
        ofile = fp.join(args.output, key)
        with codecs.open(ofile, 'w', 'utf-8') as stream:
            print("\n".join(sorted(vals)), file=stream)


if __name__ == '__main__':
    main()
