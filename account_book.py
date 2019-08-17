"""
manage account book
"""

import csv
from collections import namedtuple
from datetime import date

from date_handler import Period, Span


class Entry(namedtuple('Entry', 'date, income, outgo, groups')):
    """
    entry of account book
    
    # Attributes
    * date : date (from datetime)
    * income : int
    * outgo : int
    * groups : list
        list of groups related to the entry
    """

    def __repr__(self):
        return 'Entry(date={date}, income={income}, outgo={outgo}, groups={groups})'.format( 
            date=self.date.isoformat(), income=self.income, outgo=self.outgo, groups=self.groups)


    def filter_duration(self, begin=None, end=None):
        """
        filter Entry by duration

        # Parameters
        * begin : date
            begin of the duration
            If None, it is ignored.
        * end : date
            end of the duration
            If None, it is ignored.

        # Returns
        * _ : bool
            indicator if the condition is satisfied
        """

        if begin is None:
            begin = date.min
        if end is None:
            end = date.max
        
        return begin <= self.date <= end


    def filter_groups(self, groups=None):
        """
        helper function to filter by groups

        # Parameters
        * groups : list
            list of groups to specify entries

        # Returns
        * _ : bool
            indicator if the condition is satisfied
        """

        if groups is None:
            return True
        else:
            return all(group_self == group_arg for group_self, group_arg in zip(self.groups, groups))               


class SummaryData(namedtuple('SummaryData', 'span income outgo balance')):
    """
    summary data of account book within a span

    # Attributes
    * span : Span
        span of the summary data
    * income : int
        total income of the span
    * outgo : int
        total outgoing of the span
    * balance : int
        total balance of the span
    """

    def __repr__(self):
        span = 'from {start} to {stop}'.format(
            start=self.span.start.isoformat(), stop=self.span.stop.isoformat())
        data = 'income={income:7d} / outgo={outgo:7d} / balance={balance:7d}'.format(
            income=self.income, outgo=self.outgo, balance=self.balance)

        return span + ' : ' + data


class AccountBook:
    """
    account book

    # Attributes
    * entries : list
        list of entries, whose type is Entry
    """

    def __init__(self, entries):
        self.entries = list(entries)
        self._min_date = min(entry.date for entry in self)
        self._max_date = max(entry.date for entry in self)
    
    def __getitem__(self, position):
        return self.entries[position]


    def summarize(self, begin=None, end=None, groups=None, period='month'):
        """
        summarize the account book

        # Parameters
        * begin : date
            begin of the range
            If None, it is ignored.
        * end : date
            end of the range
            If None, it is ignored.
        * groups : list
            list of groups to filter
            If None, it is ignored.
        * bundle : str
            period of data span
            One of the following is allowed.
                * 'year'
                * 'month'
                * 'week'
                * 'day'

        # Returns
        * summary : list
            summary of the account book as a list of SummaryData
        """

        if begin is None:
            begin = self._min_date
        if end is None:
            end = self._max_date

        summary = []
        for span in Period(begin, end, period):
            start, stop = span
            income = self.sum_income(start, stop, groups)
            outgo = self.sum_outgo(start, stop, groups)
            balance = self.sum_balance(start, stop, groups)

            data = SummaryData(span, income, outgo, balance)
            summary.append(data)

        return summary


    def sum_income(self, begin=None, end=None, groups=None):
        """
        compute sum of income within a given range specified by groups

        # Parameters
        * begin : date
            begin of the range
            If None, it is ignored.
        * end : date
            end of the range
            If None, it is ignored.
        * groups : list
            list of groups to filter
            If None, it is ignored.

        # Returns
        * _ : int
            sum of income of all the entries satisfying the condition
        """

        return sum(entry.income for entry in self if entry.filter_duration(begin, end) and entry.filter_groups(groups))


    def sum_outgo(self, begin=None, end=None, groups=None):
        """
        compute sum of outgo within a given range specified by groups

        # Parameters
        * begin : date
            begin of the range
            If None, it is ignored.
        * end : date
            end of the range
            If None, it is ignored.
        * groups : list
            list of groups to filter
            If None, it is ignored.

        # Returns
        * _ : int
            sum of outgo of all the entries satisfying the condition
        """

        return sum(entry.outgo for entry in self if entry.filter_duration(begin, end) and entry.filter_groups(groups))


    def sum_balance(self, begin=None, end=None, groups=None):
        """
        compute sum of balance within a given range specified by groups

        # Parameters
        * begin : date
            begin of the range
            If None, it is ignored.
        * end : date
            end of the range
            If None, it is ignored.
        * groups : list
            list of groups to filter
            If None, it is ignored.

        # Returns
        * _ : int
            sum of balance (income minus outgo) of all the entries satisfying the condition
        """

        return sum(entry.income - entry.outgo for entry in self if entry.filter_duration(begin, end) and entry.filter_groups(groups))


def get_entries(fileobj):
    """
    get entries from a csv file
    
    # Parameters
    fileobj : file-like
        file-like object of csv file
    
    # Returns
    entries : list
        list of entries obtained from the csv file
    """

    entries = []
    read_title = False
    reader = csv.reader(fileobj)
    for row in reader:
        if not read_title:
            INDEX_DATE = row.index('日付')
            INDEX_INCOME = row.index('収入金額')
            INDEX_OUTGO = row.index('支出金額')
            INDEX_GROUP1 = row.index('大分類')
            INDEX_GROUP2 = row.index('小分類')
            read_title = True
        else:
            date = get_date(row[INDEX_DATE])
            income = int(row[INDEX_INCOME])
            outgo = int(row[INDEX_OUTGO])
            groups = [row[INDEX_GROUP1], row[INDEX_GROUP2]]

            entry = Entry(date, income, outgo, groups)
            entries.append(entry)

    return entries


def get_date(isoformat_date):
    """
    get date object from isoformat string

    # Parameters
    * isoformat_date : str
        isoformat date string (i.e. 'YYYY-MM-DD')

    # Returns
    * - : date
        date object corresponding to the input
    """

    year = int(isoformat_date[0:4])
    month = int(isoformat_date[5:7])
    day = int(isoformat_date[8:10])

    return date(year, month, day)
