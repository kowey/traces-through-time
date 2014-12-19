#!/usr/bin/env python
# pylint: disable=invalid-name
# weird filename ok because not a module
# pylint: enable=invalid-name


"""
Extract annotations from SC8 petitions files.
"""

from __future__ import print_function
from collections import defaultdict
from os import path as fp
import codecs
import glob
import re

from ttt.cli import CliConfig, iodir_argparser

_TAG_RE = re.compile(r"<(.*?)>(.*?)</\1>")


def main():
    """
    Read input dir, dump in output dir
    """
    cfg = CliConfig(description='TTT petitions metadata extractor',
                    input_description='.dat files',
                    glob='*.dat')
    psr = iodir_argparser(cfg)
    args = psr.parse_args()
    values = defaultdict(set)
    for filename in glob.glob(fp.join(args.input, cfg.glob)):
        with codecs.open(filename, 'r', 'iso8859-1') as stream:
            content = stream.read()
            for key, val in _TAG_RE.findall(content):
                values[key].add(val)
    for key, val in values.items():
        ofile = fp.join(args.output, key)
        with codecs.open(ofile, 'w', 'utf-8') as stream:
            print("\n".join(sorted(val)), file=stream)


if __name__ == '__main__':
    main()
