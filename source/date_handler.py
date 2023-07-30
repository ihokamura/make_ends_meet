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

    def __str__(self):
        if self.start == self.stop:
            return self._display_format(self.start, 'ymd')
        else:
            start = self._display_format(self.start, 'ymd')
            stop = self._display_format(self.stop, 'ymd')

            return start + '-' + stop

    def __format__(self, format_spec):
        if format_spec == 'year':
            return self._display_format(self.start, 'y')
        elif format_spec == 'month':
            return self._display_format(self.start, 'ym')
        elif format_spec == 'week':
            start = self._display_format(self.start, 'md')
            stop = self._display_format(self.stop, 'md')
            return start + '-' + stop
        elif format_spec == 'day':
            return self._display_format(self.start, 'md')
        else:
            raise ValueError('Invalid format specifier')

    @staticmethod
    def _display_format(date, flags):
        """
        construct display format of date in accordance with flags

        # Parameters
        * date : datetime.date
            date to be formatted
        * flags : str
            flags to specify the format

        # Returns
        * _ : str
            formatted string of the date
        """

        formats = {
            'y':'{:04d}'.format(date.year),
            'm':'{:02d}'.format(date.month),
            'd':'{:02d}'.format(date.day)}

        return '/'.join(formats[flag] for flag in flags)


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

    start = begin
    while True:
        increment = date(start.year + 1, 1, 1) - date(start.year, 1, 1) - date.resolution
        stop = start + increment

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

    start = begin
    while True:
        increment = date(start.year + start.month//12, start.month%12 + 1, 1) - date(start.year, start.month, 1) - date.resolution
        stop = start + increment

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

    start = begin
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
