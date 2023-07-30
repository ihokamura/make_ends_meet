"""
implement CLI version of the application
"""

from datetime import date

from account_book import AccountBook
from date_handler import Duration


COLUMN_WIDTH = 11
CATEGORIES = ('income', 'outgo', 'balance')


class CliApp:
    """
    run the application by CLI

    # Attributes
    * book : account_book.AccountBook
        account book handled by the application
    """

    def __init__(self):
        self.book = AccountBook.fromfile('source_data.csv')
        today = date.today()
        self.default_begin = date(today.year - int(today.month < 6), (today.month - 6)%12 + 1, 1)
        self.default_end = date(today.year + today.month//12, today.month%12 + 1, 1) - 1*date.resolution
        self.default_period = 'month'

    def run(self):
        """
        run CLI application

        # Parameters
        * (no parameters)

        # Returns
        * None
        """

        title_line = 'period'.rjust(COLUMN_WIDTH) + '|'
        title_line += '|'.join(category.rjust(COLUMN_WIDTH) for category in CATEGORIES)
        ruled_line = '-' * COLUMN_WIDTH + ('+' + '-' * COLUMN_WIDTH) * len(CATEGORIES)

        while True:
            try:
                duration = self.input_duration()
            except ValueError:
                # have a user input again
                continue
            except:
                # quit the application after printing a newline to make console clear
                print('')
                break

            amounts = dict()
            for category in CATEGORIES:
                amounts[category] = list(self.book.summarize_by_category(duration, category))

            print('<summary>')
            print(title_line)
            print(ruled_line)
            for i, span in enumerate(duration):
                line = format(span, duration.period).rjust(COLUMN_WIDTH)
                for category in CATEGORIES:
                    line += '|' + format(amounts[category][i], str(COLUMN_WIDTH) + 'd')
                print(line)
            print(ruled_line)

            print('Continue?')
            user_choice = input('yes/no:')
            if (len(user_choice) == 0) or (user_choice.lower()[0] != 'y'):
                # quit the application
                break


    def input_duration(self):
        """
        have a user input duration

        # Parameters
        * (no parameters)

        # Returns
        * _ : date_handler.Duration
            duration within which the account book is summarized
        """

        # input begin and end
        print('Input begin and end of summary in the format "YYYY-MM-DD".')
        begin = input_date('begin:', self.default_begin)
        end = input_date('end  :', self.default_end)
        if begin > end:
            print('[Error] begin must be less than or equal to end')
            raise ValueError

        # input period
        print('Input period of summary.')
        period = input('period:')
        if len(period) == 0:
            period = self.default_period

        try:
            return Duration(begin, end, period)
        except ValueError:
            print('[Error] invalid period')
            raise ValueError


def input_date(input_message, default_date):
    """
    have a user input date

    # Parameters
    * input_message : str
        prompt message before user input
    * default_date : datetime.date
        default date in case of empty user input

    # Returns
    * _ : datetime.date
        date converted from user input
    """

    user_input = input(input_message)
    if len(user_input) == 0:
        return default_date
    else:
        try:
            return date.fromisoformat(user_input)
        except ValueError:
            print('[Error] invalid date')
            raise ValueError
