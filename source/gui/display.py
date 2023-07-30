"""
implement display
"""

import itertools

from kivy.app import App
from kivy.graphics import Color, Line
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from gui.breakdown import BreakdownPopup


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
        self.orientation = 'lr-tb'

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
        self.orientation = 'lr-tb'
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

        for span, amount in self.plot_points:
            origin = -self.grid_values[0]/(self.grid_values[-1] - self.grid_values[0])
            value = amount/(self.grid_values[-1] - self.grid_values[0])
            self.add_widget(Bar(span=span, amount=amount, origin=origin, value=value))

    def on_grid_values(self, instance, grid_values):
        # clear canvas to update grid lines
        self.canvas.clear()

        with self.canvas:
            Color(rgba=(0, 1, 1, 0.5))
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

    amount = NumericProperty(0)
    origin = NumericProperty(0)
    value = NumericProperty(0)

    def __init__(self, *, span, amount, **kwargs):
        super(Bar, self).__init__(**kwargs)
        self.span = span
        self.amount = amount

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
