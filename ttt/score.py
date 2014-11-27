"""
Scoring against human judgements
"""

from __future__ import print_function
from collections import namedtuple
from itertools import chain

import nltk.metrics

# author: Eric Kow
# license: Public domain


# type Record = Dict String String
# type Records = Dict FilePath [Record]
# type Scores = Dict String Int -- (eg. "precision: 0.43")

_KEY_T_PREC = "text precision"
_KEY_T_REC = "text recall"
_KEY_T_F = "text f_measure"
_KEY_A_REC = "attrs recall"

SCORE_KEYS = [_KEY_T_PREC,
              _KEY_T_REC,
              _KEY_T_F,
              _KEY_A_REC]


def concat(lst):
    """
    ::

        Iterable (Iterable a) -> Iterable a
    """
    return chain.from_iterable(lst)


# data Scrutis a = Scrutis (Set a) (Set a)
class Scrutis(namedtuple('Scrutis', 'texts attrs')):
    """
    Short for scrutinees, sorry.

    Each field here consists of a set of things that be compared
    between a reference/test comparison score (eg. precision/recall)

    :param texts: set of text strings found
    :param attrs: set of attribute value pairs found
    """

    @classmethod
    def empty(cls):
        "empty instance"
        return cls(frozenset(), frozenset())


def extract_scrutis(records):
    """
    Just the evaluable items for all records (this excludes some
    things like origOccurence and appearanceDate) ::

        Records -> Dict FilePath (Scrutis String)
    """
    blacklist = [u'origOccurrence', u'appearanceDate']

    def av_pairs(rec):
        "non-boring attributes of a single record"
        return [(k, v.lower()) for k, v in rec.items()
                if k not in blacklist]

    def scrutis(recs):
        "non-boring attributes"
        text = frozenset(x.get('origOccurrence', '_ERROR_')
                         for x in recs)
        attrs = frozenset(concat(map(av_pairs, recs)))
        return Scrutis(text, attrs)

    return {p: scrutis(xs) for p, xs in records.items()}


def aggregate(dic):
    """
    Flatten a dictionary of values into a set of key,
    value pairs. This provides a possible way to aggregate
    precision/recall style scores over a set of documents.
    It may tell a different story than simply taking the
    average (which is also a bit uncertain with the NaNs
    you get when you have an empty set) ::

        Dict k (Scrutis a) -> Scrutis (FilePath, a)
    """

    def peg(scruti, key, field):
        "distribute the key for a record over all values"
        return [(key, v) for v in getattr(scruti, field)]

    def squish(field):
        """
        the basic flattening logic but focused on a
        single aspect of the thing being scrutinised
        """
        return frozenset(concat(peg(c, k, field)
                                for k, c in dic.items()))

    return Scrutis(squish('texts'), squish('attrs'))


def score_scrutis(ref, tst):
    """

    :: (Scrutis, Scrutis) -> Dict String Int
    """
    t_ref = ref.texts
    t_tst = tst.texts
    a_ref = ref.attrs
    a_tst = tst.attrs

    return {_KEY_T_PREC: nltk.metrics.precision(t_ref, t_tst),
            _KEY_T_REC: nltk.metrics.recall(t_ref, t_tst),
            _KEY_T_F: nltk.metrics.f_measure(t_ref, t_tst),
            _KEY_A_REC: nltk.metrics.recall(a_ref, a_tst)}


def score_records(reference, test):
    """
    ::

        (Records, Records) -> (Scores, Dict FilePath Scores)

    """
    empty = Scrutis.empty()
    keys = frozenset(reference.keys() + test.keys())
    ref_cmp = extract_scrutis(reference)
    tst_cmp = extract_scrutis(test)
    individual_scores = {}
    for key in sorted(keys):
        ref_mini = ref_cmp.get(key, empty)
        tst_mini = tst_cmp.get(key, empty)
        individual_scores[key] = score_scrutis(ref_mini, tst_mini)
    ref_pairs = aggregate(ref_cmp)
    tst_pairs = aggregate(tst_cmp)
    aggregate_scores = score_scrutis(ref_pairs, tst_pairs)
    return aggregate_scores, individual_scores
