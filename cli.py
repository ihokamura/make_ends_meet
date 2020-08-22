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
                duration = input_duration()
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
            if user_choice.lower()[0] != 'y':
                # quit the application
                break


def input_duration():
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
    try:
        begin = date.fromisoformat(input('begin:'))
        end = date.fromisoformat(input('end  :'))
    except ValueError:
        print('[Error] invalid date')
        raise ValueError
    if begin > end:
        print('[Error] begin must be less than or equal to end')
        raise ValueError

    # input period
    print('Input period of summary.')
    period = input('period:')
    try:
        return Duration(begin, end, period)
    except ValueError:
        print('[Error] invalid period')
        raise ValueError
