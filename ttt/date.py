"""
Stupid way of getting dates with coarse grained resolution
"""

# author: Eric Kow
# license: Public domain


from dateutil.parser import parse as dparse
import datetime
import itertools


_DEFAULT_DATE_1 = datetime.datetime(3000, 1, 1)
_DEFAULT_DATE_2 = datetime.datetime(3000, 2, 15)


def read_date(dstr):
    """
    type: `String -> String`

    Examples ::

        read_date("1432") == "1432"
        read_date("December 1432") == "1432-12"
        read_date("3 December 1432") == "1432-12-03"

    Given an English string representing a date, return an ISO formatted
    partial date representation showing only as much of the date as we
    know the granularity for.

    The underlying implementation is a bit embarassing. We're using an
    English date parser that only returns timestamps (you have to supply
    a default for fields it does not know). The approach we use is to
    parse the date *twice* and take the common prefix of their ISO
    formatted representations. Sorry.
    """

    def iso(stamp):
        "iso format for the date part only"
        return stamp.isoformat().split("T")[0]

    def common_prefix(iso1, iso2):
        "common prefix of two iso date strings"
        parts1 = iso1.split("-")
        parts2 = iso2.split("-")
        return "-".join(p1 for p1, _ in
                        itertools.takewhile(lambda (x, y): x == y,
                                            zip(parts1, parts2)))


    stamp1 = dparse(dstr, default=_DEFAULT_DATE_1)
    stamp2 = dparse(dstr, default=_DEFAULT_DATE_2)
    if not stamp1:
        return None

    return common_prefix(iso(stamp1), iso(stamp2))
