"""
run the application
"""

import sys

from cli import CliApp
from gui import GuiApp


class App:
    """
    wrap difference of user interface

    # Attributes
    * app_type : str
        type of the application
        One of the following is allowed.
        * 'cli'
        * 'gui'
    """

    def __init__(self, app_type='cli'):
        if app_type == 'cli':
            self.app = CliApp()
        else:
           self.app = GuiApp()

    def run(self):
        """
        run the application
        """

        self.app.run()


def main(app_type):
    """
    run the application

    # Parameters
    * app_type : str
        type of the application

    # Returns
    * None
    """

    app = App(app_type)
    app.run()


# message for a wrong option
USAGE = """
Usage: python3 main.py [cli|gui]
Option:
    cli: CLI version of the application
    gui: GUI version of the application
"""

if __name__ == '__main__':
    app_type = sys.argv[-1]
    if app_type in ('cli', 'gui'):
        main(app_type)
    else:
        print(USAGE)
