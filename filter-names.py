#!/usr/bin/env python
"""
Given a dictionary and a list of names,
emit a reduced list containing those which most look
like they may be names

Guesses made:

- things that appear in lowercase in the dictionary
  may just be common words

"""

from __future__ import print_function
from os import path as fp
import argparse
import os


def is_good(wordlist):
    """
    set(string) -> string -> bool

    true if a candidate should be renamed as a possible name
    """
    def inner(candidate):
        "string -> bool"
        return candidate.lower() not in wordlist
    return inner


def main():
    """
    Read input dir, dump in output dir
    """
    psr = argparse.ArgumentParser(description='TTT converter')
    psr.add_argument('wordlist', metavar='FILE',
                     type=argparse.FileType('r'),
                     help='word list (eg. /usr/share/dict/words)')
    psr.add_argument('input', metavar='FILE',
                     type=argparse.FileType('r'),
                     help='list of candidate names')
    psr.add_argument('output', metavar='DIR',
                     help='output dir')

    args = psr.parse_args()
    wordlist = frozenset(w.strip() for w in args.wordlist.readlines())
    candidates = [w.strip() for w in args.input.readlines()]

    keep = is_good(wordlist)

    retained = [c for c in candidates if keep(c)]
    rejected = [c for c in candidates if not keep(c)]

    if not fp.exists(args.output):
        os.makedirs(args.output)
    with open(fp.join(args.output, "retained.txt"), 'w') as fout:
        print("\n".join(retained), file=fout)
    with open(fp.join(args.output, "rejected.txt"), 'w') as fout:
        print("\n".join(rejected), file=fout)

main()
