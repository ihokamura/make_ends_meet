"""
implement GUI version of the application
"""

from kivy.app import App
from kivy.properties import ObjectProperty

from account_book import AccountBook
from gui.balance_chart import BalanceChart


class GuiApp(App):
    """
    run the application by GUI

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
        self.book = AccountBook.fromfile('source_data.csv')

    def build(self):
        self.balance_chart = BalanceChart(self.book)

        return self.balance_chart
