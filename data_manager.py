"""
manage data
"""

from collections import namedtuple
import csv
import datetime
from shutil import copyfile


# translation mapping
GROUP_MAIN_TRANSLATION_TABLE = {
    '収入':'income',
    '社会保障':'social security',
    '住宅':'housing',
    '生活基盤':'infrastructure',
    '通信':'communication',
    '交通':'transportation',
    '医療':'medical treatment',
    '食品':'food',
    '日用':'necessities',
    '服飾':'fashion',
    '学習':'learning',
    '投資':'investment',
    '娯楽':'recreation',
    'その他':'others'
}

GROUP_SUB_TRANSLATION_TABLE = {
    '給与':'salary',
    '賞与':'bonus',
    '時間外手当':'overtime pay',
    '住宅手当':'housing allowance',
    '通勤手当':'commutation allowance',
    '地域手当':'region allowance',
    '出張手当':'travel allowance',
    '経費':'company expense',
    '代休控除':'deduction by holiday adjustment',
    '所得税':'income tax',
    '住民税':'resident tax',
    '年金':'pension',
    '健康保険':'health insurance',
    '雇用保険':'unemployment insurance',
    '家賃':'house rent',
    '保証金':'guaranty money',
    '修繕':'house repairs',
    'ガス':'gas bill',
    '電気':'electricity bill',
    '水道':'warter bill',
    '携帯電話':'cellphone',
    'インターネット':'internet',
    '定期券':'commuter ticket',
    '公共交通':'public transportation',
    '病院':'hospital',
    '薬局':'drug store',
    '食材・調味料':'foodstuffs',
    '惣菜':'prepared food',
    '日用品':'daily necessities',
    '家具':'furniture',
    '家電製品':'electrical appliances',
    '電子機器':'electronic equipment',
    '衣服・靴':'clothing and shoes',
    '調髪':'haircut',
    'クリーニング':'cleaning',
    '鞄・アクセサリ':'bag and accessories',
    '外食':'food service',
    'レジャー':'leisure',
    '書籍・雑誌':'book and magazine',
    '資格試験':'qualification examination',
    '投資信託':'investment trust',
    '会費':'membership fee',
    '手数料':'service charge',
    '寄付':'donation',
    'その他':'others'
}


# groups classification
GROUPS_CLASSIFICATION = {
    'income':
    (
        'salary',
        'bonus',
        'overtime pay',
        'housing allowance',
        'commutation allowance',
        'region allowance',
        'travel allowance',
        'company expense',
        'deduction by holiday adjustment',
        'others'
    ),
    'social security':
    (
        'income tax',
        'resident tax',
        'pension',
        'health insurance',
        'unemployment insurance',
        'others'
    ),
    'housing':
    (
        'house rent',
        'guaranty money',
        'house repairs',
        'others'
    ),
    'infrastructure':
    (
        'gas bill',
        'electricity bill',
        'warter bill',
        'others'
    ),
    'communication':
    (
        'cellphone',
        'internet',
        'others'
    ),
    'transportation':
    (
        'commuter ticket',
        'public transportation',
        'others'
    ),
    'medical treatment':
    (
        'hospital',
        'drug store',
        'others'
    ),
    'food':
    (
        'foodstuffs',
        'prepared food',
        'others'
    ),
    'necessities':
    (
        'daily necessities',
        'furniture',
        'electrical appliances',
        'electronic equipment',
        'others'
    ),
    'fashion':
    (
        'clothing and shoes',
        'haircut',
        'cleaning',
        'bag and accessories',
        'others'
    ),
    'learning':
    (
        'book and magazine',
        'qualification examination',
        'others'
    ),
    'investment':
    (
        'investment trust',
        'others'
    ),
    'recreation':
    (
        'membership fee',
        'service charge',
        'others'
    ),
    'others':
    (
        'food service',
        'leisure',
        'donation',
        'others'
    )
}


# tuple of groups related to the entry
Groups = namedtuple('Groups', 'main, sub')


class Entry(namedtuple('Entry', 'date, income, outgo, groups')):
    """
    represent entry of account book
    
    # Attributes
    * date : datetime.date
    * income : int
    * outgo : int
    * groups : Groups
        tuple of groups related to the entry
    """

    def __repr__(self):
        return 'Entry(date={date}, income={income}, outgo={outgo}, groups={groups})'.format( 
            date=self.date.isoformat(), income=self.income, outgo=self.outgo, groups=self.groups)

    def is_in_span(self, span):
        """
        indicate if Entry is in span

        # Parameters
        * span : date_handler.Span
            span to check the entry

        # Returns
        * _ : bool
            indicator if the condition is satisfied
        """

        return span.start <= self.date <= span.stop

    def is_in_groups(self, groups=None):
        """
        indicate if Entry is in groups

        # Parameters
        * groups : iterable
            groups to check the entry

        # Returns
        * _ : bool
            indicator if the condition is satisfied
            If `groups` is `None`, the function returns `True`.
        """

        if groups is None:
            return True
        else:
            return all(group_self == group_arg for group_self, group_arg in zip(self.groups, groups))               


def generate_entries(file):
        """
        generate entries from a file
        
        # Parameters
        file : str
            name of csv file
        
        # Yields
        _ : Entry
            entries of account book
        """

        # copy the original file for fail-safe
        tmp_file = 'tmp.csv'
        copyfile(file, tmp_file)

        with open(file=tmp_file, mode='r', encoding='utf-8') as fileobj:
            reader = csv.reader(fileobj)

            # get indices from header
            header = next(reader)
            index_date = header.index('日付')
            index_income = header.index('収入金額')
            index_outgo = header.index('支出金額')
            index_group_main = header.index('大分類')
            index_group_sub = header.index('小分類')

            # read each rows to yield entries of account book
            for row in reader:
                date = datetime.date.fromisoformat(row[index_date])
                income = int(row[index_income])
                outgo = int(row[index_outgo])
                groups = Groups(GROUP_MAIN_TRANSLATION_TABLE[row[index_group_main]], GROUP_SUB_TRANSLATION_TABLE[row[index_group_sub]])

                yield Entry(date, income, outgo, groups)
