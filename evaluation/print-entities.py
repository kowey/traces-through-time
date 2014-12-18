#!/usr/bin/env python

# pylint: disable=invalid-name
# pylint: enable=invalid-name

"""
Given a directory of annotated texts (where interesting
text spans are surrounded by <>), generate a json file
for each text in the style of nimrodel
"""


from __future__ import print_function
from os import path as fp
import codecs
import json
import os

from ttt.cli import CliConfig, iodir_argparser, read_records


def save_occurrences(input_dir, output_dir, subpath):
    """
    Given input and output dirs, and a subpath within the
    input dir, read json, dump original occurences as text
    """
    ifilename = fp.join(input_dir, subpath)
    ofilename = fp.join(output_dir, subpath)
    with open(ifilename, 'rb') as istream:
        jdicts = json.load(istream)
        insts = [x.get('origOccurrence', '') for x in jdicts]
        with codecs.open(ofilename, 'w', 'utf-8') as ostream:
            print("\n".join(insts), file=ostream)


def main():
    "read cli args, loop on dir"
    cfg = CliConfig(description='crude annotations viewer',
                    input_description='annotation json',
                    glob='*')
    psr = iodir_argparser(cfg)
    args = psr.parse_args()
    output_dir = args.output
    for root, _, files in os.walk(args.input):
        root_subpath = fp.relpath(root, args.input)
        oroot = fp.join(output_dir, root_subpath)
        if not fp.exists(oroot):
            os.makedirs(oroot)
        for bname in files:
            save_occurrences(root, oroot, bname)

if __name__ == '__main__':
    main()
