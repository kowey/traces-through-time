"""
Stupid way of getting dates with coarse grained resolution
"""

# author: Eric Kow
# license: Public domain


from dateutil.parser import parse as dparse
import datetime
import itertools


_FAR_AWAY = 9999
_DEFAULT_DATE_1 = datetime.datetime(_FAR_AWAY, 1, 1)
_DEFAULT_DATE_2 = datetime.datetime(_FAR_AWAY, 2, 15)


def read_date(dstr, prefix=None, **kwargs):
    """
    type: `String -> String`

    Examples ::

        read_date("1432") == "1432"
        read_date("December 1432") == "1432-12"
        read_date("3 December 1432") == "1432-12-03"
        read_date("December", prefix="1311") == "1311-12"

    Given an English string representing a date, return an ISO formatted
    partial date representation showing only as much of the date as we
    know the granularity for. (If you supply a prefix, it will be used
    to provide a partial default for unknown values)

    Note that we also accept dateutil.parse args (`fuzzy` may be of use)

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


    if prefix is not None:
        try:
            default1 = dparse(prefix, default=_DEFAULT_DATE_1)
            default2 = dparse(prefix, default=_DEFAULT_DATE_2)
        except TypeError as _:
            raise ValueError("Could not parse prefix date {}".format(prefix))
    else:
        default1 = _DEFAULT_DATE_1
        default2 = _DEFAULT_DATE_2
	
    try:
        stamp1 = dparse(dstr, default=default1, **kwargs)
        stamp2 = dparse(dstr, default=default2, **kwargs)
    except (TypeError, ValueError) as _:
        return None

    res = common_prefix(iso(stamp1), iso(stamp2))
    if res == str(_FAR_AWAY):
        res = None
    return res
