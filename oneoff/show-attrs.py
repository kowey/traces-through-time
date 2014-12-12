# display all attributes used in a list of json dictionaries
# author: Eric Kow
# license: Public domain

from __future__ import print_function
import json
import sys

from ttt.keys import KEYS


def pretty(record):
    "eric-friendly string representation of a json record"

    def withadj(key):
        "attribute with an adjective variant"
        noun = record[key]
        adj = record.get("adjective" + key)  # can be None
        if noun and adj:
            return "%s: %s [%s]" % (key, noun, adj)
        elif noun:
            return "%s: %s" % (key, noun)
        else:
            return None

    return "\n".join(x for x in map(withadj, KEYS) if x is not None)


def main(ipath):
    "print out each record in the file, and also set of keys"

    with open(ipath) as ifile:
        records = list(json.load(ifile))
        for rec in records:
            print(pretty(rec))
            print()

        attrs = (frozenset(d) for d in records)
        print(frozenset.union(*attrs))


main(sys.argv[1])
