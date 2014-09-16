#!/usr/bin/env python

"""
Given a directory of badly formatted json output files,
(strings contain illegal characters), produce a directory
of hopefully better files.

This is just simple character substitution, replacing all
newlines with spaces
"""


from __future__ import print_function
from os import path as fp
import argparse
import glob
import os
import re


def fix_json(bad_str):
    """
    Given file content as a string, return a fixed string
    """
    def norm_space(matchobj):
        "replace all whitespace by single space"
        before = matchobj.group(0)
        after = " ".join(before.split())
        return after
    qt_re = re.compile(r'".*?"', flags=re.DOTALL)
    return qt_re.sub(norm_space, bad_str)


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
    for filename in glob.glob(fp.join(args.input, '*')):
        with open(filename) as ifile:
            ofilename = fp.join(args.output,
                                fp.basename(filename))
            filestr = ifile.read()
            with open(ofilename, 'w') as ofile:
                print(fix_json(filestr), file=ofile)


main()
