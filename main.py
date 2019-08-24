"""
run the application
"""

from cli import CliApp
# from gui import GuiApp


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

    def __init__(self, app_type='gui'):
#       if app_type == 'cli':
#           self.app = CliApp()
#       else:
#          self.app = GuiApp()
        self.app = CliApp()

    def run(self):
        """
        run the application
        """

        self.app.run()


def main(app_type='gui'):
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


if __name__ == '__main__':
    main(app_type='cli')
