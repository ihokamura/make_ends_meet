"""
implement CLI version of the application
"""

from datetime import date

from account_book import AccountBook
from date_handler import Duration


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

        while True:
            try:
                duration = input_duration()
                category = input_category()
            except ValueError:
                # have a user input again
                continue
            except:
                # quit the application after printing a newline to make console clear
                print('')
                break

            ruled_line = '-' * 20
            print(ruled_line)
            for span, amount in zip(duration, self.book.summarize_by_category(duration, category)):
                print(format(span, duration.period) + format(amount, '7d'))
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
        end = date.fromisoformat(input('end:'))
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


def input_category():
    """
    have a user input category

    # Parameters
    * (no parameters)

    # Returns
    * category : str
        category by which the account book is summarized
    """

    # input category
    print('Input category of summary(income/outgo/balance).')
    category = input('category:')
    if category in ('income', 'outgo', 'balance'):
        return category
    else:
        print('[Error] invalid category')
        raise ValueError
