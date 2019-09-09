"""
manage account book
"""

from collections import defaultdict

from data_manager import generate_entries
from date_handler import Duration, Span


class AccountBook:
    """
    account book

    # Attributes
    * entries : iterable
        entries of account book, whose type is data_manager.Entry
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
        * _ : AccountBook
            AccountBook object corresponding to the file
        """

        return cls(generate_entries(file))

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
        * _ : int
            sum of the category within the duration
        """

        sum_category = self._sum_category[category]
        for span in duration:
            yield sum_category(span)

    def get_breakdown(self, span):
        """
        get breakdown within the span

        # Parameters
        * span : date_handler.Span
            span of breakdown

        # Returns
        * breakdown : collections.defaultdict
            dictionary mapping group to amount within the span
        """

        breakdown = defaultdict(int)

        for entry in self:
            if span.start <= entry.date <= span.stop:
                breakdown[entry.groups[0]] += (entry.income + entry.outgo)

        return breakdown

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
