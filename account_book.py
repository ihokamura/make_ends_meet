"""
manage account book
"""

from collections import namedtuple
import csv
import datetime
from shutil import copyfile

from date_handler import Duration, Span


class Entry(namedtuple('Entry', 'date, income, outgo, groups')):
    """
    represent entry of account book
    
    # Attributes
    * date : datetime.date
    * income : int
    * outgo : int
    * groups : tuple
        tuple of groups related to the entry
    """

    def __repr__(self):
        return 'Entry(date={date}, income={income}, outgo={outgo}, groups={groups})'.format( 
            date=self.date.isoformat(), income=self.income, outgo=self.outgo, groups=self.groups)

    def is_in_span(self, span):
        """
        indicate if Entry is in span

        # Parameters
        * span : date_handler.Span
            span to check the entry

        # Returns
        * _ : bool
            indicator if the condition is satisfied
        """

        return span.start <= self.date <= span.stop

    def is_in_groups(self, groups=None):
        """
        indicate if Entry is in groups

        # Parameters
        * groups : iterable
            groups to check the entry

        # Returns
        * _ : bool
            indicator if the condition is satisfied
            If `groups` is `None`, the function returns `True`.
        """

        if groups is None:
            return True
        else:
            return all(group_self == group_arg for group_self, group_arg in zip(self.groups, groups))               


SummaryData = namedtuple('SummaryData', 'span amount')


class AccountBook:
    """
    account book

    # Attributes
    * entries : iterable
        entries of account book, whose type is Entry
    """

    def __init__(self, entries):
        self.entries = list(entries)
        self._sum_category = {'income':self._sum_income, 'outgo':self._sum_outgo, 'balance':self._sum_balance}

    def __iter__(self):
        return iter(self.entries)

    @classmethod
    def fromfile(cls, file):
        """
        construct from a file

        # Parameters
        * file : str
            name of the file

        # Returns
        * book : AccountBook
            AccountBook object corresponding to the file
        """

        # copy the original file for fail-safe
        TMP_FILE = 'tmp.csv'
        copyfile(file, TMP_FILE)

        with open(file=TMP_FILE, mode='r', encoding='utf-8') as fileobj:
            entry = cls._generate_entries(fileobj)
            book = cls(entry)

        return book

    @classmethod
    def _generate_entries(cls, fileobj):
        """
        generate entries from a file
        
        # Parameters
        fileobj : file-like
            file-like object of csv file
        
        # Yields
        _ : Entry
            entries of account book
        """

        reader = csv.reader(fileobj)

        # get indices from header
        header = next(reader)
        INDEX_DATE = header.index('日付')
        INDEX_INCOME = header.index('収入金額')
        INDEX_OUTGO = header.index('支出金額')
        INDEX_GROUP1 = header.index('大分類')
        INDEX_GROUP2 = header.index('小分類')

        # read each rows to yield entries of account book
        for row in reader:
            date = datetime.date.fromisoformat(row[INDEX_DATE])
            income = int(row[INDEX_INCOME])
            outgo = int(row[INDEX_OUTGO])
            groups = tuple(row[i] for i in (INDEX_GROUP1, INDEX_GROUP2))

            yield Entry(date, income, outgo, groups)

    def summarize_by_category(self, duration, category):
        """
        summarize the account book by category

        # Parameters
        * duration : date_handler.Duration
            duration of summary
        * category : str
            category of summary
            One of the following is allowed.
            * 'income'
            * 'outgo'
            * 'balance'

        # Yields
        * _ : SummaryData
            summary data of the account book within the duration
        """

        sum_category = self._sum_category[category]
        for span in duration:
            amount = sum_category(span)
            yield SummaryData(span, amount)

    def _sum_income(self, span, groups=None):
        """
        compute sum of income filtered by span and groups

        # Parameters
        * span : date_handler.Span
            span to filter entries
        * groups : tuple
            tuple of groups to filter entries
            If None, it is ignored.

        # Returns
        * _ : int
            sum of income of all the entries satisfying the condition
        """

        return sum(
            entry.income for entry in self
            if entry.is_in_span(span) and entry.is_in_groups(groups))

    def _sum_outgo(self, span, groups=None):
        """
        compute sum of outgo filtered by span and groups

        # Parameters
        * span : date_handler.Span
            span to filter entries
        * groups : tuple
            tuple of groups to filter entries
            If None, it is ignored.

        # Returns
        * _ : int
            sum of outgo of all the entries satisfying the condition
        """

        return sum(
            entry.outgo for entry in self
            if entry.is_in_span(span) and entry.is_in_groups(groups))

    def _sum_balance(self, span, groups=None):
        """
        compute sum of balance filtered by span and groups

        # Parameters
        * span : date_handler.Span
            span to filter entries
        * groups : tuple
            tuple of groups to filter entries
            If None, it is ignored.

        # Returns
        * _ : int
            sum of balance (income minus outgo) of all the entries satisfying the condition
        """

        return sum(
            entry.income - entry.outgo for entry in self
            if entry.is_in_span(span) and entry.is_in_groups(groups))
