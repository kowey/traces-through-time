#!/usr/bin/env python

"""
Tidy up the whitespace in the input directory,
with some simple sentence segmentation along the way
for readability

NB: files are assumed to be UTF-8 encoded
"""

from __future__ import print_function
from os import path as fp
import argparse
import codecs
import glob
import os

import nltk.data

from ttt.reflow import reflow


def do_file(tokenizer, ifile, output_dir):
    """
    Read input file, write modified version to output dir with
    same basename
    """
    ofile = fp.join(output_dir, fp.basename(ifile))
    with codecs.open(ifile, 'r', 'utf-8') as stream_in:
        itext = stream_in.read()
        otext = reflow(tokenizer, itext)
        with codecs.open(ofile, 'w', 'utf-8') as stream_out:
            print(otext, file=stream_out)


def main():
    """
    Read input dir, dump in output dir
    """
    psr = argparse.ArgumentParser(description='text reflow')
    psr.add_argument('input', metavar='DIR', help='dir with text files')
    psr.add_argument('output', metavar='DIR', help='output directory')
    psr.add_argument('--tokenizer', metavar='FILE',
                     default='tokenizers/punkt/english.pickle',
                     help='pickle for NLTK sentence tokenizer')
    args = psr.parse_args()

    tokenizer = nltk.data.load(args.tokenizer)

    if not fp.exists(args.output):
        os.makedirs(args.output)
    for ifile in glob.glob(fp.join(args.input, '*')):
        do_file(tokenizer, ifile, args.output)

if __name__ == '__main__':
    main()
