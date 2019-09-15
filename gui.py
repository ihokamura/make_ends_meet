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
from kivy.graphics import Color, Line
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
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


class Display(FloatLayout):
    """
    widget to display change of amounts
    """

    def __init__(self, **kwargs):
        super(Display, self).__init__(**kwargs)

    def plot_chart(self, spans, values):
        """
        plot bar chart to display change of amounts

        # Parameters
        * spans : list
            list of spans
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
        period = App.get_running_app().balance_chart.duration.period
        self.x_axis.labels = list(format(span, period) for span in spans)
        self.y_axis.grid_values = grid_values
        self.plot_area.grid_values = grid_values
        self.plot_area.plot_points = list(zip(spans, values))


class XAxis(GridLayout):
    """
    widget for x-axis

    # Attributes
    * labels : ListProperty
        list of labels
    """

    labels = ListProperty(list())

    def __init__(self, **kwargs):
        super(XAxis, self).__init__(**kwargs)
        self.orientation = 'horizontal'

    def on_labels(self, instance, labels):
        # remove all Label objects to update labels
        self.clear_widgets()

        for label in self.labels:
            label_widget = Label(text=label)
            self.add_widget(label_widget)


class YAxis(Widget):
    """
    widget for y-axis

    # Attributes
    * grid_values : ListProperty
        list of grid values
    * label_widgets : dict
        dictionary mapping grid value to Label object
    """

    grid_values = ListProperty(list())

    def __init__(self, **kwargs):
        super(YAxis, self).__init__(**kwargs)
        self.label_widgets = dict()

    def on_height(self, instance, height):
        self._update()

    def on_grid_values(self, instance, grid_values):
        # remove all Label objects to update scales
        self.clear_widgets()
        self.label_widgets.clear()

        for gv in self.grid_values:
            label_widget = Label(text=str(gv))
            self.add_widget(label_widget)
            self.label_widgets[gv] = label_widget
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
            self.label_widgets[gv].center_x = self.center_x
            self.label_widgets[gv].center_y = self.y + self.height*(gv - self.grid_values[0])/(self.grid_values[-1] - self.grid_values[0])


class PlotArea(GridLayout):
    """
    widget for y-axis

    # Attributes
    * plot_points : ListProperty
        list of plot points
    * grid_values : ListProperty
        list of grid values
    * lines : dict
        dictionary mapping grid value to Line object
    """

    plot_points = ListProperty(list())
    grid_values = ListProperty(list())

    def __init__(self, **kwargs):
        super(PlotArea, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.lines = dict()

    def on_size(self, instance, size):
        self._update()
        # expand width of parent if there is not enough space to display all the bars
        self.parent.width = max(
            self.parent.width,
            self.col_default_width * len(self.plot_points))

    def on_plot_points(self, instance, plot_points):
        # remove all Bar objects to update chart
        self.clear_widgets()

        # restore default width of parent if there is enough space to display all the bars
        self.parent.width = max(
            App.get_running_app().balance_chart.display.width * 0.9,
            self.col_default_width * len(self.plot_points))

        for span, v in self.plot_points:
            origin = -self.grid_values[0]/(self.grid_values[-1] - self.grid_values[0])
            value = v/(self.grid_values[-1] - self.grid_values[0])
            self.add_widget(Bar(span=span, origin=origin, value=value))

    def on_grid_values(self, instance, grid_values):
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

    def __init__(self, *, span, **kwargs):
        super(Bar, self).__init__(**kwargs)
        self.span = span

    def on_touch_down(self, touch):
        if self.is_valid_touch(touch):
            self.show_breakdown()

    def is_valid_touch(self, touch):
        """
        check if the touch is valid

        # Parameters
        * touch : MouseMotionEvent
            touch event

        # Returns
        * _ : bool
            indicator if the touch is valid or not
        """

        return abs(touch.x - (self.x + self.width * 0.5)) < self.width * 0.1

    def show_breakdown(self):
        """
        show breakdown

        # Parameters
        * (no parameter)

        # Returns
        * None
        """

        popup = BreakdownPopup(span=self.span, pos_hint={'x':0.5, 'y':0.5}, size_hint=(0.5, 0.5))
        popup.open()


class BreakdownPopup(Popup):
    """
    widget for breakdown popup
    """

    def __init__(self, *, span, **kwargs):
        super(BreakdownPopup, self).__init__(**kwargs)
        self.title_align = 'center'
        self.duration_list = list(span for span in App.get_running_app().balance_chart.duration)
        self.update(span)

    def update(self, span):
        """
        update breakdown popup

        # Parameters
        * span : date_handler.span
            new span of this popup

        # Returns
        * None
        """

        self.span = span
        self.title = str(self.span)
        self.content = BreakdownContent(span=self.span)
        self.content.close_button.bind(on_release=self.dismiss)
        self.content.prev_button.bind(on_release=self.show_prev)
        self.content.next_button.bind(on_release=self.show_next)

    def show_prev(self, obj):
        """
        show breakdown of the previous span

        # Parameters
        * obj : Object
            object invoking this function

        # Returns
        * None
        """

        prev_span = self.duration_list[self.duration_list.index(self.span) - 1]
        self.update(prev_span)

    def show_next(self, obj):
        """
        show breakdown of the previous span

        # Parameters
        * obj : Object
            object invoking this function

        # Returns
        * None
        """

        next_span = self.duration_list[(self.duration_list.index(self.span) + 1) % len(self.duration_list)]
        self.update(next_span)


class BreakdownContent(FloatLayout):
    """
    widget for content of breakdown popup
    """

    def __init__(self, *, span, **kwargs):
        super(BreakdownContent, self).__init__(**kwargs)
        self.make_table(span)
    
    def make_table(self, span):
        """
        make table of breakdown details

        # Parameters
        * span : date_handler.Span
            span of the breakdown

        # Returns
        * None
        """

        breakdown = App.get_running_app().book.get_breakdown(span)
        for number, (group, amount) in enumerate(sorted(breakdown.items())):
            if number % 2 == 1:
                background_color = [0.5, 0.5, 0.5, 0.25]
            else:
                background_color = [0, 0, 0, 0]

            group_label = BreakdownEntry(text=group, halign='left', background_color=background_color)
            self.table.add_widget(group_label)

            amount_label = BreakdownEntry(text=str(amount), halign='right', background_color=background_color)
            self.table.add_widget(amount_label)


class BreakdownEntry(Label):
    """
    widget for an entry of breakdown table

    # Attributes
    * background_color : ListProperty
        background color of the entry represented as rgba
    """

    background_color = ListProperty(None)


class GuiApp(App):
    """
    run the application by CLI

    # Attributes
    * balance_chart : ObjectProperty
        BalanceChart object handled by the application
    * book : account_book.AccountBook
        account book handled by the application
    """

    balance_chart = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GuiApp, self).__init__(**kwargs)
        self.title = 'make ends meet'
        self.book = account_book.AccountBook.fromfile('source_data.csv')

    def build(self):
        Builder.load_file('chart.kv')
        self.balance_chart = BalanceChart(self.book)

        return self.balance_chart
