"""
Create a sort of regression test suite by unpacking a large JSON file
(containing outputs from the previous system) into two directories,
one containing just the text for all "origOccurence"s found and one
containing the corresponding json dictionary.

This gives us the possibility of doing some sort of before and after
comparison on our respective outputs given the same text fragments
"""



# author: Eric Kow
# license: Public domain

from __future__ import print_function
from os import path as fp
import codecs
import argparse
import os
import json
import math


def main():
    "print out each record in the file, and also set of keys"

    psr = argparse.ArgumentParser(description='TTT regression suite writer')
    psr.add_argument('input', metavar='FILE', help='json file (list of dict)')
    psr.add_argument('output', metavar='DIR', help='output directory')
    args = psr.parse_args()

    text_dir = fp.join(args.output, "text")
    before_dir = fp.join(args.output, "json-before")

    with open(args.input) as ifile:
        records = list(json.load(ifile))
        digits = int(math.log10(len(records))) + 1
        for i, rec in enumerate(records):
            bname = str(i).zfill(digits) + ".txt"
            dname = bname[:2]
            text_subdir = fp.join(text_dir, dname)
            before_subdir = fp.join(before_dir, dname)
            if not fp.exists(text_subdir):
                os.makedirs(text_subdir)
            if not fp.exists(before_subdir):
                os.makedirs(before_subdir)

            with codecs.open(fp.join(text_subdir, bname),
                             'w', 'utf-8') as tfile:
                print(rec.get("origOccurrence", ""), file=tfile)
            with open(fp.join(before_subdir, bname), 'wb') as jfile:
                json.dump(rec, jfile)


main()
