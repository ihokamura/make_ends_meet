"""
initialize gui module
"""

import os

# suppress kivy log
os.environ['KIVY_NO_FILELOG'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '1'

from kivy.base import Builder

# import gui modules and load kv files to define classes
import gui.balance_chart
import gui.breakdown
import gui.dashboard
import gui.display


Builder.load_file('gui/balance_chart.kv')
Builder.load_file('gui/breakdown.kv')
Builder.load_file('gui/dashboard.kv')
Builder.load_file('gui/display.kv')
