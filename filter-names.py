#!/usr/bin/env python
"""
Given a dictionary and a list of names,
emit a reduced list containing those which most look
like they may be names

Guesses made:

- things which do not appear in the stop list
- things that appear in lowercase in the dictionary
  may just be common words
- things may be plural forms of words in the dictionary
  (cheap and morphologically naive guessing)

"""

from __future__ import print_function
from os import path as fp
import argparse
import os


def is_good(wordlist, stoplist):
    """
    set(string) -> string -> bool

    true if a candidate should be renamed as a possible name
    """
    def inner(candidate):
        "string -> bool"
        lcand = candidate.lower()
        lcands = [lcand]
        if lcand.endswith("es"):
            lcands.append(lcand[:-2])
        if lcand.endswith("s"):
            lcands.append(lcand[:-1])
        if lcand.endswith("ing"):
            stem = lcand[:-3]
            lcands.extend([stem, stem+"e"])
        return lcand not in stoplist and\
            not any(l for l in lcands if l in wordlist)
    return inner


def main():
    """
    Read input dir, dump in output dir
    """
    psr = argparse.ArgumentParser(description='TTT name filter')
    psr.add_argument('wordlist', metavar='FILE',
                     type=argparse.FileType('r'),
                     help='word list (eg. /usr/share/dict/words)')
    psr.add_argument('--stop', metavar='FILE',
                     type=argparse.FileType('r'),
                     help='words to reject (case insensitive text list)')
    psr.add_argument('input', metavar='FILE',
                     type=argparse.FileType('r'),
                     help='list of candidate names')
    psr.add_argument('output', metavar='DIR',
                     help='output dir')

    args = psr.parse_args()
    wordlist = frozenset(w.strip() for w in args.wordlist.readlines())
    candidates = [w.strip() for w in args.input.readlines()]
    stoplist = frozenset(w.strip().lower() for w in args.stop.readlines())\
        if args.stop else frozenset()

    keep = is_good(wordlist, stoplist)

    retained = [c for c in candidates if keep(c)]
    rejected = [c for c in candidates if not keep(c)]

    if not fp.exists(args.output):
        os.makedirs(args.output)
    with open(fp.join(args.output, "retained.txt"), 'w') as fout:
        print("\n".join(retained), file=fout)
    with open(fp.join(args.output, "rejected.txt"), 'w') as fout:
        print("\n".join(rejected), file=fout)

main()
