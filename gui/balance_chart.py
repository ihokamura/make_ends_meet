"""
implement balance chart
"""

import calendar
import datetime

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.uix.widget import Widget

import date_handler


class BalanceChart(Widget):
    """
    root widget of GUI

    # Attributes
    * duration : date_handler.Duration
        duration of summary the chart shows
    * category : str
        category of summary the chart shows
    * book : account_book.AccountBook
        account book handled by the application
    * updater : BalanceChartUpdater
        event dispatcher to update the chart
    """

    def __init__(self, book, **kwargs):
        super(BalanceChart, self).__init__(**kwargs)
        self.book = book
        self.updater = BalanceChartUpdater()

        # set default values
        year, month = datetime.date.today().year, datetime.date.today().month
        begin = datetime.date(year, month, 1)
        end = datetime.date(year, month, calendar.monthlen(year, month))
        self.duration = date_handler.Duration(begin, end)
        self.category = 'balance'

        # initialize user interface after creating the instance
        init_trigger = Clock.create_trigger(self.init_ui)
        init_trigger()

    def init_ui(self, dt=0):
        """
        initialize user interface

        # Parameters
        * dt : int
            time in seconds between function call and start of the actual process
            It should be 0 unless there is some reason to delay the initialization.

        # Returns
        * None
        """

        # initialize date range and period
        self.dashboard.date_range.begin.date = self.duration.begin
        self.dashboard.date_range.end.date = self.duration.end
        self.dashboard.period_selector.select_period(self.duration.period)

        # initialize category
        # bind callbacks here to update graph only once (i.e. when setting category)
        self.updater.bind(
            on_category=self.update_category,
            on_period=self.update_period,
            on_date_range=self.update_date_range)
        self.dashboard.category_selector.select_category(self.category)

    def update_date_range(self, dispatcher, *, begin, end):
        """
        update range of date

        # Parameters
        * dispatcher : EventDispatcher
            event dispatcher which invokes this function
        * begin : datetime.date
        * end : datetime.date
        """

        # save the current period and make a new Duration object
        period = self.duration.period
        self.duration = date_handler.Duration(begin, end, period)
        self.update_chart()

    def update_period(self, dispatcher, *, period):
        """
        update period

        # Parameters
        * dispatcher : EventDispatcher
            event dispatcher which invokes this function
        * period : str
        """

        # save the current begin and end and make a new Duration object
        begin, end = self.duration.begin, self.duration.end
        self.duration = date_handler.Duration(begin, end, period)
        self.update_chart()

    def update_category(self, dispatcher, *, category):
        """
        update category

        # Parameters
        * dispatcher : EventDispatcher
            event dispatcher which invokes this function
        * category : str
        """

        self.category = category
        self.update_chart()

    def update_chart(self):
        """
        update chart

        # Parameters
        * num_of_data : int
            number of data(labels)
            If it is 0, the number of data is automatically determined by period.

        # Returns
        * None
        """

        spans = list(span for span in self.duration)
        amounts = list(self.book.summarize_by_category(self.duration, self.category))

        self.display.plot_chart(spans, amounts)


class BalanceChartUpdater(EventDispatcher):
    """
    event dispatcher to update BalanceChart
    """

    def __init__(self, **kwargs):
        super(BalanceChartUpdater, self).__init__(**kwargs)
        self.register_event_type('on_date_range')
        self.register_event_type('on_period')
        self.register_event_type('on_category')

    def on_date_range(self, *, begin, end):
        """
        callback which responds to a change of range of date

        # Parameters
        * begin : datetime.date
        * end : datetime.date

        # Returns
        * None
        """

        pass

    def on_period(self, *, period):
        """
        callback which responds to a change of period

        # Parameters
        * period : str

        # Returns
        * None
        """

        pass

    def on_category(self, *, category):
        """
        callback which responds to a change of category

        # Parameters
        * category : str

        # Returns
        * None
        """

        pass
