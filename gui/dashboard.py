"""
implement dashboard
"""

import calendar
import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget


class DateRange(BoxLayout):
    """
    widget to set range of date
    """

    def __init__(self, **kwargs):
        super(DateRange, self).__init__(**kwargs)

    def update_date_range(self, selector):
        """
        update range of date

        # Parameters
        * (no parameters)

        # Returns
        * None
        """

        if self.begin.date > self.end.date:
            if selector == self.begin:
                self.end.date = self.begin.date
            else:
                self.begin.date = self.end.date

        updater = App.get_running_app().balance_chart.updater
        updater.dispatch('on_date_range', begin=self.begin.date, end=self.end.date)


class DateSelector(Widget):
    """
    widget to select a date

    # Attributes
    * date : datetime.date
        current selected date
    """

    def __init__(self, **kwargs):
        super(DateSelector, self).__init__(**kwargs)

    @property
    def date(self):
        """
        get date from spinners

        # Parameters
        * (no parameters)

        # Returns
        * _ : datetime.date
            current selected date
        """

        return datetime.date(
            int(self.year_spinner.text),
            int(self.month_spinner.text),
            int(self.day_spinner.text))

    @date.setter
    def date(self, date):
        """
        set date to spinners

        # Parameters
        * date : datetime.date
            date to be set

        # Returns
        * None
        """

        self.year_spinner.text = str(date.year)
        self.month_spinner.text = str(date.month)
        self.day_spinner.text = str(date.day)

    def update_year(self):
        """
        update year

        # Parameters
        * (no parameters)

        # Returns
        * None
        """

        self._set_day_values()
        self.parent.update_date_range(self)

    def update_month(self):
        """
        update month

        # Parameters
        * (no parameters)

        # Returns
        * None
        """

        self._set_day_values()
        self.parent.update_date_range(self)

    def update_day(self):
        """
        update day

        # Parameters
        * (no parameters)

        # Returns
        * None
        """

        self.parent.update_date_range(self)

    def _set_day_values(self):
        """
        set values of day spinner

        # Parameters
        * (no parameters)

        # Returns
        * None
        """

        last = calendar.monthlen(int(self.year_spinner.text), int(self.month_spinner.text))
        self.day_spinner.values = tuple(str(d) for d in range(1, last + 1))
        if int(self.day_spinner.text) > last:
            self.date = datetime.date(int(self.year_spinner.text), int(self.month_spinner.text), last)


class CategorySelector(BoxLayout):
    """
    widget to select a category

    # Attributes
    * category : str
        current selected category
    """

    def __init__(self, category='balance', **kwargs):
        super(CategorySelector, self).__init__(**kwargs)
        self.category = category
        self._selectors = dict()
        init_trigger = Clock.create_trigger(self.init_selectors)
        init_trigger()

    def init_selectors(self, dt=0):
        """
        initialize selectors, which maps category to button

        # Parameters
        * dt : int
            time in seconds between function call and start of the actual process
            It should be 0 unless there is some reason to delay the initialization.

        # Returns
        * None
        """

        for category in ('income', 'outgo', 'balance'):
            self._selectors[category] = getattr(self, category)

    def select_category(self, category):
        """
        select a category

        # Parameters
        * category : str

        # Returns
        * None
        """

        self._selectors[category].state = 'down'


class CategoryToggle(ToggleButton):
    """
    toggle button to select a category
    """

    def __init__(self, **kwargs):
        super(CategoryToggle, self).__init__(**kwargs)
        self.group = 'category'

    def on_state(self, instance, state):
        if state == 'down':
            # invoke callback to update category
            updater = App.get_running_app().balance_chart.updater
            updater.dispatch('on_category', category=self.text)


class PeriodSelector(BoxLayout):
    """
    widget to select a period
    """

    def __init__(self, period='month', **kwargs):
        super(PeriodSelector, self).__init__(**kwargs)
        self.period = period
        self._selectors = dict()
        Clock.schedule_once(self.init_selectors)

    def init_selectors(self, dt=0):
        """
        initialize selectors, which maps period to button

        # Parameters
        * dt : int
            time in seconds between function call and start of the actual process
            It should be 0 unless there is some reason to delay the initialization.

        # Returns
        * None
        """

        for period in ('day', 'week', 'month', 'year'):
            self._selectors[period] = getattr(self, period)

    def select_period(self, period):
        """
        select a period

        # Parameters
        * period : str

        # Returns
        * None
        """

        self._selectors[period].state = 'down'


class PeriodToggle(ToggleButton):
    """
    toggle button to select a period
    """

    def __init__(self, **kwargs):
        super(PeriodToggle, self).__init__(**kwargs)
        self.group = 'period'

    def on_state(self, instance, state):
        if state == 'down':
            # invoke callback to update category
            updater = App.get_running_app().balance_chart.updater
            updater.dispatch('on_period', period=self.text)
