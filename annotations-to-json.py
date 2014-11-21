#!/usr/bin/env python

"""
Given a directory of annotated texts (where interesting
text spans are surrounded by <>), generate a json file
for each text in the style of nimrodel
"""


from __future__ import print_function
from os import path as fp
import codecs
import json
import re

from ttt.cli import CliConfig, iodir_argparser, generic_main


_BRACKET_RE = re.compile(r'men')


def mk_json(input_dir, output_dir, subpath):
    """
    Given input and output dirs, and a subpath within the
    input dir, read annotations, and save as json records
    with just an 'origOccurrence' member.
    """
    ifilename = fp.join(input_dir, subpath)
    ofilename = fp.join(output_dir, subpath)
    with codecs.open(ifilename, 'r', 'utf-8') as istream:
        txt = istream.read()
        matches = re.findall(r'<(.*?)>', txt)
        jdicts = [{'origOccurrence': x} for x in matches]
        with open(ofilename, 'wb') as ostream:
            json.dump(jdicts, ostream)


def main():
    "read cli args, loop on dir"
    cfg = CliConfig(description='annotations converter',
                    input_description='annotated text files',
                    glob='*')
    psr = iodir_argparser(cfg)
    args = psr.parse_args()
    generic_main(cfg, mk_json, args)

if __name__ == '__main__':
    main()
