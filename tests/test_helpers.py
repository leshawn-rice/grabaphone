from unittest import TestCase
from datetime import date
from api.helpers import convert_to_date, make_date_valid


class ConvertToDateTestCase(TestCase):
    '''convert_to_date Test Case'''

    def test_valid_dates(self):
        '''Returns valid date: valid str'''
        dates_to_check = ['January 8, 1984', 'Dec 9, 2000',
                          'December 2020', 'March, 2021', '2010']
        for raw_date in dates_to_check:
            converted_date = convert_to_date(raw_date)
            self.assertIsInstance(converted_date, date)
            # Regex matches XXXX-XX-XX i.e. 2020-08-21
            self.assertRegex(f'{converted_date}',
                             r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$')

    def test_invalid_str(self):
        '''Returns January 1900: invalid str'''
        converted_date = convert_to_date('not-a-date')
        self.assertIsInstance(converted_date, date)
        # Regex matches XXXX-XX-XX i.e. 2020-08-21
        self.assertEqual(f'{converted_date}', '1900-01-01')

    def test_no_date(self):
        '''Returns January 1900: no param'''
        converted_date = convert_to_date()
        self.assertIsInstance(converted_date, date)
        # Regex matches XXXX-XX-XX i.e. 2020-08-21
        self.assertEqual(f'{converted_date}', '1900-01-01')

    def test_invalid_type_int(self):
        '''Returns January 1900: param of type int'''
        converted_date = convert_to_date(24)
        self.assertIsInstance(converted_date, date)
        # Regex matches XXXX-XX-XX i.e. 2020-08-21
        self.assertEqual(f'{converted_date}', '1900-01-01')

    def test_invalid_type_bool(self):
        '''Returns January 1900: param of type boolean'''
        converted_date = convert_to_date(True)
        self.assertIsInstance(converted_date, date)
        # Regex matches XXXX-XX-XX i.e. 2020-08-21
        self.assertEqual(f'{converted_date}', '1900-01-01')


class MakeDateValidTestCase(TestCase):
    '''make_date_valid Test Case'''

    def test_official(self):
        '''Removes (Official) from date_str'''

        valid_str = make_date_valid('(Official) January 2021')
        self.assertEqual(valid_str, 'January 2021')

    def test_q1(self):
        '''Replaces Q1 with January in date_str'''

        valid_str = make_date_valid('Q1 2021')
        self.assertEqual(valid_str, 'January 2021')

    def test_q2(self):
        '''Replaces Q2 with April in date_str'''

        valid_str = make_date_valid('Q2 2021')
        self.assertEqual(valid_str, 'April 2021')

    def test_q3(self):
        '''Replaces Q3 with July in date_str'''

        valid_str = make_date_valid('Q3 2021')
        self.assertEqual(valid_str, 'July 2021')

    def test_q4(self):
        '''Replaces Q4 with October in date_str'''

        valid_str = make_date_valid('Q4 2021')
        self.assertEqual(valid_str, 'October 2021')

    def test_yes(self):
        '''Replaces Yes with January 1900 in date_str'''

        valid_str = make_date_valid('Yes')
        self.assertEqual(valid_str, 'January 1900')

    def test_no_data(self):
        '''Returns None with no params'''

        self.assertIsNone(make_date_valid())

    def test_invalid_type_int(self):
        '''Returns None with invalid type int'''

        self.assertIsNone(make_date_valid(7))

    def test_invalid_type_int(self):
        '''Returns None with invalid type bool'''

        self.assertIsNone(make_date_valid(True))
