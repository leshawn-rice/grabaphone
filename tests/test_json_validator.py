from unittest import TestCase
from api.JSONValidator import Validator
from api.models import Manufacturer, Device
from tests.setup_tests import db, seed_db


class ConvertNumTestCase(TestCase):
    '''convert_num Test Case'''

    def test_valid_no_constraints(self):
        '''Returns 7: just passing args num='7' '''
        converted = Validator.convert_num(num='7')
        self.assertEqual(converted, 7)

    def test_valid_min(self):
        '''Returns 12: passing args minimum=5 & num='12' '''
        converted = Validator.convert_num(minimum=5, num='12')
        self.assertEqual(converted, 12)

    def test_valid_min_max(self):
        '''Returns 8: passing args minimum=5, maximum=10, & num='8' '''
        converted = Validator.convert_num(minimum=5, maximum=10, num='8')
        self.assertEqual(converted, 8)

    def test_valid_min_max_default(self):
        '''Returns 43: passing args minimum=0, maximum=100, default=0, & num='43' '''
        converted = Validator.convert_num(
            minimum=0, maximum=100, default=0, num='43')
        self.assertEqual(converted, 43)

    def test_under_min(self):
        '''Returns 10: passing args minimum=10 & num='4' '''
        converted = Validator.convert_num(minimum=10, num='4')
        self.assertEqual(converted, 10)

    def test_over_max(self):
        '''Returns 10: passing args maximum=10 & num='15' '''
        converted = Validator.convert_num(maximum=10, num='15')
        self.assertEqual(converted, 10)

    def test_invalid_no_default(self):
        '''Returns None: passing args num=False '''
        converted = Validator.convert_num(num=False)
        self.assertIsNone(converted)

    def test_invalid_with_default(self):
        '''Returns 10: passing args num=False & default=10 '''
        converted = Validator.convert_num(num=False, default=10)
        self.assertEqual(converted, 10)

    def test_invalid_no_args(self):
        '''Returns None: passing no args'''
        converted = Validator.convert_num()
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
        is_valid = Validator.check_name('Apple', Manufacturer)
        self.assertTrue(is_valid)
        is_valid = Validator.check_name('Samsung', Manufacturer)
        self.assertTrue(is_valid)
        is_valid = Validator.check_name('Google', Manufacturer)
        self.assertTrue(is_valid)

    def test_valid_devices(self):
        '''Returns True: valid device name'''
        is_valid = Validator.check_name('iPhone', Device)
        self.assertTrue(is_valid)
        is_valid = Validator.check_name('Galaxy', Device)
        self.assertTrue(is_valid)
        is_valid = Validator.check_name('Pixel', Device)
        self.assertTrue(is_valid)

    def test_valid_mismatch_case(self):
        '''Returns True: valid name with mismatched case'''
        is_valid = Validator.check_name('aPpLE', Manufacturer)
        self.assertTrue(is_valid)
        is_valid = Validator.check_name('SAmSUng', Manufacturer)
        self.assertTrue(is_valid)
        is_valid = Validator.check_name('IphOnE', Device)
        self.assertTrue(is_valid)
        is_valid = Validator.check_name('galAXy', Device)
        self.assertTrue(is_valid)

    def test_invalid_manufacturer(self):
        '''Returns False: invalid name'''
        is_valid = Validator.check_name('Invalid-Device', Manufacturer)
        self.assertFalse(is_valid)

    def test_invalid_device(self):
        '''Returns False: invalid name'''
        is_valid = Validator.check_name('Invalid-Device', Device)
        self.assertFalse(is_valid)

    def test_invalid_type_int(self):
        '''Returns False: integer'''
        is_valid = Validator.check_name(7, Manufacturer)
        self.assertFalse(is_valid)
        is_valid = Validator.check_name(7, Device)
        self.assertFalse(is_valid)

    def test_invalid_type_bool(self):
        '''Returns False: boolean'''
        is_valid = Validator.check_name(False, Manufacturer)
        self.assertFalse(is_valid)
        is_valid = Validator.check_name(True, Manufacturer)
        self.assertFalse(is_valid)
        is_valid = Validator.check_name(False, Device)
        self.assertFalse(is_valid)
        is_valid = Validator.check_name(True, Device)
        self.assertFalse(is_valid)

    def test_invalid_type_none_name(self):
        '''Returns False: nonetype'''
        is_valid = Validator.check_name(None, Manufacturer)
        self.assertFalse(is_valid)
        is_valid = Validator.check_name(None, Device)
        self.assertFalse(is_valid)

    def test_invalid_type_none_model(self):
        '''Returns False: nonetype args'''
        is_valid = Validator.check_name('Apple', None)
        self.assertFalse(is_valid)
        is_valid = Validator.check_name('iPhone', None)
        self.assertFalse(is_valid)

    def test_invalid_type_no_args(self):
        '''Returns False: no args'''
        is_valid = Validator.check_name()
        self.assertFalse(is_valid)
        is_valid = Validator.check_name()
        self.assertFalse(is_valid)

    def tearDown(self):
        db.session.rollback()


class CheckConvertableTestCase(TestCase):
    '''Validator.check_convertable Test Case'''

    def test_valid_type_str(self):
        '''Returns True: valid limit'''
        is_valid = Validator.check_convertable('17')
        self.assertTrue(is_valid)

    def test_valid_type_int(self):
        '''Returns True: valid limit of type int'''
        is_valid = Validator.check_convertable(21)
        self.assertTrue(is_valid)

    def test_invalid_type_str(self):
        '''Returns False: invalid limit'''
        is_valid = Validator.check_convertable('NaN')
        self.assertFalse(is_valid)

    def test_invalid_type_bool(self):
        '''Returns False: boolean'''
        is_valid = Validator.check_convertable(True)
        self.assertFalse(is_valid)
        is_valid = Validator.check_convertable(False)
        self.assertFalse(is_valid)

    def test_invalid_type_none(self):
        '''Returns False: nonetype'''
        is_valid = Validator.check_convertable(None)
        self.assertFalse(is_valid)

    def test_invalid_type_no_args(self):
        '''Returns False: no args'''
        is_valid = Validator.check_convertable()
        self.assertFalse(is_valid)


class SanitizeJSONTestCase(TestCase):
    '''sanitize_json Test Case'''

    @classmethod
    def setUpClass(cls):
        db.drop_all()
        db.create_all()
        seed_db()

    def setUp(self):
        self.jsonValidator = Validator()
        self.json_data = {
            'manufacturer': 'Apple',
            'name': 'iPhone',
            'offset': '0',
            'limit': '100',
            'is_released': 'True'
        }
        self.default = {
            'manufacturer': None,
            'name': None,
            'offset': 0,
            'limit': 100,
            'is_released': None
        }

    def test_valid_json(self):
        '''
        Returns data of correct types and values on valid data
        '''
        new_data = self.jsonValidator.sanitize_json(
            data=self.json_data, valid_params=[*self.json_data.keys()])
        self.assertEqual({
            'manufacturer': 'Apple',
            'name': 'iPhone',
            'offset': 0,
            'limit': 100,
            'is_released': True
        }, new_data)

    def test_invalid_values(self):
        '''
        Returns data of default types and values on invalid data
        '''
        self.json_data = {
            'manufacturer': 'Test Manufacturer Plus',
            'name': 'Test Grabaphone phone 0100',
            'offset': '-5',
            'limit': '1032',
            'is_released': None
        }
        new_data = self.jsonValidator.sanitize_json(
            data=self.json_data, valid_params=[*self.json_data.keys()])
        self.assertEqual(self.default, new_data)

    def test_invalid_type_none(self):
        '''
        Returns default data with NoneType values
        '''
        self.json_data = {
            'manufacturer': None,
            'name': None,
            'offset': None,
            'limit': None,
            'is_released': None
        }
        new_data = self.jsonValidator.sanitize_json(
            data=self.json_data, valid_params=[*self.json_data.keys()])
        self.assertEqual(self.default, new_data)

    def test_invalid_type_no_args(self):
        '''
        Returns default data with no args
        '''
        new_data = self.jsonValidator.sanitize_json()
        self.assertEqual({}, new_data)
        new_data = self.jsonValidator.sanitize_json(
            valid_params=[*self.json_data.keys()])
        self.assertEqual({}, new_data)

    def tearDown(self):
        db.session.rollback()
