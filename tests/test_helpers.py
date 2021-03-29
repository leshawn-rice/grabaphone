from unittest import TestCase
from datetime import date
from api.models import Manufacturer, Device
from api.helpers import check_name, check_convertable, convert_num
from api.helpers import convert_to_date, make_date_valid
from api.helpers import sanitize_json, validate_json
from tests.setup_tests import db, seed_db


'''Functions
check_manuf_name: y
check_convertable: y
convert_to_date: y
make_date_valid: y
sanitize_json: x
validate_json: x
'''


class ConvertNumTestCase(TestCase):
    '''convert_num Test Case'''

    def test_valid_no_constraints(self):
        '''Returns 7: just passing args num='7' '''
        converted = convert_num(num='7')
        self.assertEqual(converted, 7)

    def test_valid_min(self):
        '''Returns 12: passing args minimum=5 & num='12' '''
        converted = convert_num(minimum=5, num='12')
        self.assertEqual(converted, 12)

    def test_valid_min_max(self):
        '''Returns 8: passing args minimum=5, maximum=10, & num='8' '''
        converted = convert_num(minimum=5, maximum=10, num='8')
        self.assertEqual(converted, 8)

    def test_valid_min_max_default(self):
        '''Returns 43: passing args minimum=0, maximum=100, default=0, & num='43' '''
        converted = convert_num(minimum=0, maximum=100, default=0, num='43')
        self.assertEqual(converted, 43)

    def test_under_min(self):
        '''Returns 10: passing args minimum=10 & num='4' '''
        converted = convert_num(minimum=10, num='4')
        self.assertEqual(converted, 10)

    def test_over_max(self):
        '''Returns 10: passing args maximum=10 & num='15' '''
        converted = convert_num(maximum=10, num='15')
        self.assertEqual(converted, 10)

    def test_invalid_no_default(self):
        '''Returns None: passing args num=False '''
        converted = convert_num(num=False)
        self.assertIsNone(converted)

    def test_invalid_with_default(self):
        '''Returns 10: passing args num=False & default=10 '''
        converted = convert_num(num=False, default=10)
        self.assertEqual(converted, 10)

    def test_invalid_no_args(self):
        '''Returns None: passing no args'''
        converted = convert_num()
        self.assertIsNone(converted)


class CheckNameTestCase(TestCase):
    '''check_name Test Case'''

    @classmethod
    def setUpClass(cls):
        db.drop_all()
        db.create_all()
        seed_db()

    def test_valid_manufacturers(self):
        '''Returns True: valid manufacturer name'''
        is_valid = check_name('Apple', Manufacturer)
        self.assertTrue(is_valid)
        is_valid = check_name('Samsung', Manufacturer)
        self.assertTrue(is_valid)
        is_valid = check_name('Google', Manufacturer)
        self.assertTrue(is_valid)

    def test_valid_devices(self):
        '''Returns True: valid device name'''
        is_valid = check_name('iPhone', Device)
        self.assertTrue(is_valid)
        is_valid = check_name('Galaxy', Device)
        self.assertTrue(is_valid)
        is_valid = check_name('Pixel', Device)
        self.assertTrue(is_valid)

    def test_valid_mismatch_case(self):
        '''Returns True: valid name with mismatched case'''
        is_valid = check_name('aPpLE', Manufacturer)
        self.assertTrue(is_valid)
        is_valid = check_name('SAmSUng', Manufacturer)
        self.assertTrue(is_valid)
        is_valid = check_name('IphOnE', Device)
        self.assertTrue(is_valid)
        is_valid = check_name('galAXy', Device)
        self.assertTrue(is_valid)

    def test_invalid_manufacturer(self):
        '''Returns False: invalid name'''
        is_valid = check_name('Invalid-Device', Manufacturer)
        self.assertFalse(is_valid)

    def test_invalid_device(self):
        '''Returns False: invalid name'''
        is_valid = check_name('Invalid-Device', Device)
        self.assertFalse(is_valid)

    def test_invalid_type_int(self):
        '''Returns False: integer'''
        is_valid = check_name(7, Manufacturer)
        self.assertFalse(is_valid)
        is_valid = check_name(7, Device)
        self.assertFalse(is_valid)

    def test_invalid_type_bool(self):
        '''Returns False: boolean'''
        is_valid = check_name(False, Manufacturer)
        self.assertFalse(is_valid)
        is_valid = check_name(True, Manufacturer)
        self.assertFalse(is_valid)
        is_valid = check_name(False, Device)
        self.assertFalse(is_valid)
        is_valid = check_name(True, Device)
        self.assertFalse(is_valid)

    def test_invalid_type_none_name(self):
        '''Returns False: nonetype'''
        is_valid = check_name(None, Manufacturer)
        self.assertFalse(is_valid)
        is_valid = check_name(None, Device)
        self.assertFalse(is_valid)

    def test_invalid_type_none_model(self):
        '''Returns False: nonetype args'''
        is_valid = check_name('Apple', None)
        self.assertFalse(is_valid)
        is_valid = check_name('iPhone', None)
        self.assertFalse(is_valid)

    def test_invalid_type_no_args(self):
        '''Returns False: no args'''
        is_valid = check_name()
        self.assertFalse(is_valid)
        is_valid = check_name()
        self.assertFalse(is_valid)

    def tearDown(self):
        db.session.rollback()


class CheckConvertableTestCase(TestCase):
    '''check_convertable Test Case'''

    def test_valid_type_str(self):
        '''Returns True: valid limit'''
        is_valid = check_convertable('17')
        self.assertTrue(is_valid)

    def test_valid_type_int(self):
        '''Returns True: valid limit of type int'''
        is_valid = check_convertable(21)
        self.assertTrue(is_valid)

    def test_invalid_type_str(self):
        '''Returns False: invalid limit'''
        is_valid = check_convertable('NaN')
        self.assertFalse(is_valid)

    def test_invalid_type_bool(self):
        '''Returns False: boolean'''
        is_valid = check_convertable(True)
        self.assertFalse(is_valid)
        is_valid = check_convertable(False)
        self.assertFalse(is_valid)

    def test_invalid_type_none(self):
        '''Returns False: nonetype'''
        is_valid = check_convertable(None)
        self.assertFalse(is_valid)

    def test_invalid_type_no_args(self):
        '''Returns False: no args'''
        is_valid = check_convertable()
        self.assertFalse(is_valid)


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


class SanitizeJSONTestCase(TestCase):
    '''sanitize_json Test Case'''

    @classmethod
    def setUpClass(cls):
        db.drop_all()
        db.create_all()
        seed_db()

    def setUp(self):
        self.json_data = {
            'manufacturer': 'Apple',
            'name': 'iPhone',
            'offset': 0,
            'limit': 100,
            'is_released': 'True'
        }

    def test_valid_json(self):
        new_data = sanitize_json(self.json_data)
        print(new_data)
        self.assertTrue(True)

    def tearDown(self):
        db.session.rollback()
