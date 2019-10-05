"""
implement breakdown popup
"""

from kivy.app import App
from kivy.properties import ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup


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
