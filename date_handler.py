"""
handle date
"""

from collections import namedtuple
from datetime import date


# span of date
Span = namedtuple('Span', 'start stop')

class Period:
    """
    generator which periodically yields spans

    # Attributes
    * begin : date
        begin of the generation
    * end : date
        end of the generation
    * period : str
        period of spans
        One of the following is allowed.
        * 'year'
        * 'month'
        * 'week'
        * 'day'
    """

    def __init__(self, begin, end, period='month'):
        self.begin = begin
        self.end = end
        self.period = period
        self._yield_func = YIELD_FUNC_DICT[period]

    def __iter__(self):
        return self._yield_func(self.begin, self.end)


# dictionary mapping period to generator function
YIELD_FUNC_DICT = dict()
def register_yield_func(period):
    """
    register a generator function which yields a span

    # Parameters
    * period : str
        period of spans
        One of the following is allowed.
        * 'year'
        * 'month'
        * 'week'
        * 'day'

    # Returns
    * decorate
        function object which actually registers the generator function
    """

    def decorate(yield_func):
        """
        decorator to register a generator function

        # Parameters
        * yield_func
            generator function which yields a Span object

        # Returns
        * None
        """

        YIELD_FUNC_DICT[period] = yield_func

    return decorate


@register_yield_func('year')
def yield_span_year(begin, end):
    """
    yield spans in a year period

    # Parameters
    * begin : date
        begin of the generation
    * end : date
        end of the generation

    # Yields
    * _ : Span
        spans within the range in a year period
    """

    y = begin.year
    while True:
        start = date(y, 1, 1)
        stop = date(y + 1, 1, 1) - date.resolution

        yield Span(start, stop)

        if end < stop:
            break
        else:
            y = y + 1


@register_yield_func('month')
def yield_span_month(begin, end):
    """
    yield spans in a month period

    # Parameters
    * begin : date
        begin of the generation
    * end : date
        end of the generation

    # Yields
    * _ : Span
        spans within the range in a month period
    """

    y, m = begin.year, begin.month
    while True:
        start = date(y, m, 1)
        if m == 12:
            y, m = y + 1, 1
        else:
            m = m + 1
        stop = date(y, m, 1) - date.resolution

        yield Span(start, stop)

        if end < stop:
            break


@register_yield_func('week')
def yield_span_week(begin, end):
    """
    yield spans in a week period

    # Parameters
    * begin : date
        begin of the generation
    * end : date
        end of the generation

    # Yields
    * _ : Span
        spans within the range in a week period
    """

    start = begin - date.resolution * begin.weekday()
    while True:
        stop = start + date.resolution * 6

        yield Span(start, stop)

        if end < stop:
            break
        else:
            start = stop + date.resolution


@register_yield_func('day')
def yield_span_day(begin, end):
    """
    yield spans in a day period

    # Parameters
    * begin : date
        begin of the generation
    * end : date
        end of the generation

    # Yields
    * _ : Span
        spans within the range in a day period
    """

    start = begin
    while True:
        stop = start

        yield Span(start, stop)

        if end < stop:
            break
        else:
            start = stop + date.resolution
