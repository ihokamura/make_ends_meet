"""
main of the application
"""

from datetime import date
from shutil import copyfile

from account_book import AccountBook, get_entries


def prepare_AccountBook(filename):
    """
    prepare workspace for a given csv file

    # Parameters
    * filename : str
        name of input csv file

    # Returns
    * book : AccountBook
        AccountBook object corresponding to the csv file
    """

    TMP_FILE_NAME = "tmp.csv"
    copyfile(filename, TMP_FILE_NAME)

    with open(file=TMP_FILE_NAME, mode='r', encoding='utf-8') as fileobj:
        entry = get_entries(fileobj)
        book = AccountBook(entry)

    return book


def main():
    """
    main function of the application

    # Parameters
    * (no parameters)

    # Returns
    * None
    """

    SRC_FILE_NAME = "source_data.csv"
    book = prepare_AccountBook(SRC_FILE_NAME)

    begin = date(2019,1,1)
    end = None
    groups = None
    period = 'month'
 
    summary = book.summarize(begin, end, groups, period)
    for data in summary:
        print(data)


if __name__ == '__main__':
    main()
