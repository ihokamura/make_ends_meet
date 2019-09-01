"""
implement GUI version of the application
"""

import calendar
import datetime
import itertools
import os

# suppress kivy log
os.environ['KIVY_NO_FILELOG'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivy.app import App
from kivy.base import Builder
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.graphics import Color, Line, Rotate
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

import account_book
import date_handler


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
        self.duration = date_handler.Duration(datetime.date.today(), datetime.date.today())
        self.category = 'balance'
        self.book = book
        self.updater = BalanceChartUpdater()

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

    def update_category(self, *args, category):
        """
        update category

        # Parameters
        * dispatcher : EventDispatcher
            event dispatcher which invokes this function
        * category : str
        """

        self.category = category
        self.update_chart()

    def update_chart(self, num_of_data=0):
        """
        update chart

        # Parameters
        * num_of_data : int
            number of data(labels)
            If it is 0, the number of data is automatically determined by period.

        # Returns
        * None
        """

        if num_of_data == 0:
            mapping = {'year':5, 'month':6, 'week':5, 'day':7}
            num_of_data = mapping[self.duration.period]

        labels = list(format(span, self.duration.period) for span in self.duration)[-num_of_data:]
        amounts = list(self.book.summarize_by_category(self.duration, self.category))[-num_of_data:]

        self.display.plot_chart(labels, amounts)


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

        self.parent.parent.parent.updater.dispatch('on_date_range', begin=self.begin.date, end=self.end.date)


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

        _, last = calendar.monthrange(int(self.year_spinner.text), int(self.month_spinner.text))
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

    def on_state(self, instance, value):
        if value == 'down':
            # invoke callback to update category
            self.parent.parent.parent.parent.updater.dispatch('on_category', category=self.text)


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

    def on_state(self, instance, value):
        if value == 'down':
            # invoke callback to update category
            self.parent.parent.parent.parent.updater.dispatch('on_period', period=self.text)


class Display(FloatLayout):
    """
    widget to display change of amounts
    """

    def __init__(self, **kwargs):
        super(Display, self).__init__(**kwargs)

    def plot_chart(self, labels, values):
        """
        plot bar chart to display change of amounts

        # Parameters
        * labels : list
            list of labels
        * values : list
            list of values

        # Returns
        * None
        """

        values_max = max(max(values), 0)
        values_min = min(min(values), 0)

        # set step size
        # step is determined so that
        # * step == floor(log10(values_min)) if values_max == 0
        # * step == floor(log10(values_max)) if values_min == 0
        # * step == max(floor(log10(values_min)), floor(log10(values_max))) otherwise
        for n in itertools.count():
            v = (n % 9 + 1) * 10**(n // 9)
            if v > values_max:
                step_pos = 10**(n // 9)
                break
        for n in itertools.count():
            v = -((n % 9 + 1) * 10**(n // 9))
            if v <= values_min:
                step_neg = 10**(n // 9)
                break
        step = max(step_neg, step_pos)

        # set start and stop
        for v in itertools.count(step=-step):
            if v <= values_min:
                start = v
                break
        for v in itertools.count(step=step):
            if v > values_max:
                stop = v + 1
                break

        # save grid values
        grid_values = list(range(start, stop, step))

        # update display
        self.x_axis.labels = labels
        self.y_axis.grid_values = grid_values
        self.plot_area.grid_values = grid_values
        self.plot_area.plot_values = values


class XAxis(BoxLayout):
    """
    widget for x-axis

    # Properties
    * labels : list
        list of labels
    """

    labels = ListProperty(list())

    def __init__(self, **kwargs):
        super(XAxis, self).__init__(**kwargs)
        self.orientation = 'horizontal'

    def on_labels(self, instance, value):
        # remove all Label objects to update labels
        self.clear_widgets()
        for l in self.labels:
            self.add_widget(Label(text=l))


class YAxis(Widget):
    """
    widget for y-axis

    # Properties
    * grid_values : list
        list of grid values

    # Attributes
    * labels : dict
        dictionary mapping grid value to Label object
    """

    grid_values = ListProperty(list())

    def __init__(self, **kwargs):
        super(YAxis, self).__init__(**kwargs)
        self.labels = dict()

    def on_size(self, instance, value):
        self._update()

    def on_grid_values(self, instance, value):
        # remove all Label objects to update scales
        self.clear_widgets()
        for gv in self.grid_values:
            label = Label(text=str(gv))
            self.add_widget(label)
            self.labels[gv] = label
        self._update()

    def _update(self):
        """
        update y-axis

        # Parameters
        * (no parameters)

        # Returns
        * None
        """

        for gv in self.grid_values:
            self.labels[gv].center_x = self.center_x
            self.labels[gv].center_y = self.y + self.height*(gv - self.grid_values[0])/(self.grid_values[-1] - self.grid_values[0])


class PlotArea(BoxLayout):
    """
    widget for y-axis

    # Properties
    * plot_values : list
        list of plot values
    * grid_values : list
        list of grid values

    # Attributes
    * lines : dict
        dictionary mapping grid value to Line object
    """

    plot_values = ListProperty(list())
    grid_values = ListProperty(list())

    def __init__(self, **kwargs):
        super(PlotArea, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.lines = dict()

    def on_size(self, instance, value):
        self._update()

    def on_plot_values(self, instance, value):
        # remove all Bar objects to update bars
        self.clear_widgets()
        for v in self.plot_values:
            origin = -self.grid_values[0]/(self.grid_values[-1] - self.grid_values[0])
            value = v/(self.grid_values[-1] - self.grid_values[0])
            self.add_widget(Bar(origin=origin, value=value))

    def on_grid_values(self, instance, value):
        # clear canvas to update grid lines
        self.canvas.clear()
        with self.canvas:
            Color(rgba=(0, 1, 1, 1))
            for gv in self.grid_values:
                line = Line(width=1.5)
                self.lines[gv] = line
        self._update()

    def _update(self):
        """
        update y-axis

        # Parameters
        * (no parameters)

        # Returns
        * None
        """

        for gv in self.grid_values:
            y = self.y + self.height*(gv - self.grid_values[0])/(self.grid_values[-1] - self.grid_values[0])
            self.lines[gv].points = [self.x, y, self.right, y]


class Bar(Widget):
    """
    widget to draw a bar of graph

    # Attributes
    * origin : NumericProperty
        origin of the bar
    * value : NumericProperty
        value of the bar
    """

    origin = NumericProperty(0)
    value = NumericProperty(0)


class GuiApp(App):
    """
    run the application by CLI

    # Attributes
    * book : account_book.AccountBook
        account book handled by the application
    """

    def __init__(self, **kwargs):
        super(GuiApp, self).__init__(**kwargs)
        self.title = 'make ends meet'
        self.book = account_book.AccountBook.fromfile('source_data.csv')

    def build(self):
        Builder.load_file('chart.kv')
        root = BalanceChart(self.book)
        return root