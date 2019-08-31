"""
handle date
"""

import calendar
from collections import namedtuple
from datetime import date


class Span(namedtuple('Span', 'start stop')):
    """
    represent span of date

    # Attributes
    * start : datetime.date
    * stop : datetime.date
    """

    def __format__(self, format_spec):
        if format_spec == 'year':
            return str(self.start.isoformat()[:4])
        elif format_spec == 'month':
            return str(self.start.isoformat()[2:7].replace('-', '/'))
        elif format_spec == 'week':
            start = self.start.isoformat()[5:].replace('-', '/')
            stop = self.stop.isoformat()[5:].replace('-', '/')
            return start + '-' + stop
        elif format_spec == 'day':
            return str(self.start.isoformat()[5:].replace('-', '/'))
        else:
            raise ValueError('Invalid format specifier')


class Duration:
    """
    yield spans periodically

    # Attributes
    * begin : datetime.date
        begin of the duration
    * end : datetime.date
        end of the duration
    * period : str
        period of spans
        One of the following is allowed.
        * 'year'
        * 'month'
        * 'week'
        * 'day'
    """

    # dictionary mapping period to generator function
    _span_generators = dict()

    def __init__(self, begin, end, period='month'):
        if begin > end:
            raise ValueError('begin must be less than or equal to end')
        self.begin = begin
        self.end = end

        try:
            self._generate_span = self._span_generators[period]
        except:
            raise ValueError('invalid literal for period: \'{p}\''.format(p=period))
        self.period = period

    def __iter__(self):
        return self._generate_span(self.begin, self.end)

    @classmethod
    def span_generator(cls, period):
        """
        register a generator function which yields spans

        # Parameters
        * period : str
            period of spans

        # Returns
        * register : function
            function object which actually registers the generator function
        """

        def register(span_generator):
            """
            register a generator function

            # Parameters
            * span_generator
                generator function which yields a Span object

            # Returns
            * None
            """

            cls._span_generators[period] = span_generator

        return register


@Duration.span_generator('year')
def generate_year_span(begin, end):
    """
    yield spans in a year period

    # Parameters
    * begin : datetime.date
        begin of the duration
    * end : datetime.date
        end of the duration

    # Yields
    * _ : Span
        spans within the duration in a year period
    """

    start = date(begin.year, 1, 1)
    while True:
        stop = date(start.year, 12, 31)

        yield Span(start, stop)

        if stop >= end:
            break
        else:
            start = stop + date.resolution


@Duration.span_generator('month')
def generate_month_span(begin, end):
    """
    yield spans in a month period

    # Parameters
    * begin : datetime.date
        begin of the duration
    * end : datetime.date
        end of the duration

    # Yields
    * _ : Span
        spans within the duration in a month period
    """

    start = date(begin.year, begin.month, 1)
    while True:
        stop = start + (calendar.monthrange(start.year, start.month)[1] - 1)*date.resolution

        yield Span(start, stop)

        if stop >= end:
            break
        else:
            start = stop + date.resolution


@Duration.span_generator('week')
def generate_week_span(begin, end):
    """
    yield spans in a week period

    # Parameters
    * begin : datetime.date
        begin of the duration
    * end : datetime.date
        end of the duration

    # Yields
    * _ : Span
        spans within the duration in a week period
    """

    start = begin - begin.weekday()*date.resolution
    while True:
        stop = start + 6*date.resolution

        yield Span(start, stop)

        if stop >= end:
            break
        else:
            start = stop + date.resolution


@Duration.span_generator('day')
def generate_day_span(begin, end):
    """
    yield spans in a day period

    # Parameters
    * begin : datetime.date
        begin of the duration
    * end : datetime.date
        end of the duration

    # Yields
    * _ : Span
        spans within the duration in a day period
    """

    start = begin
    while True:
        stop = start

        yield Span(start, stop)

        if stop >= end:
            break
        else:
            start = stop + date.resolution
