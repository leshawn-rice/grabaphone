from unittest import TestCase
from app.app import app
from app.database import db
from api.models import Manufacturer
from api.helpers import check_manuf_name, check_limit

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///grabaphone_test-db'


def seed_db():
    mock_manufs = {
        'Apple': 'https://apple.com',
        'Samsung': 'https://samsung.com',
        'Google': 'https://google.com'
    }
    for name, url in mock_manufs.items():
        manuf = Manufacturer(name=name, url=url)
        db.session.add(manuf)
        db.session.commit()


class CheckManufNameTestCase(TestCase):
    '''check_manuf_name Test Case'''

    @classmethod
    def setUpClass(cls):
        db.drop_all()
        db.create_all()
        seed_db()

    def test_valid_manufacturer(self):
        '''Returns True: valid name'''
        is_valid = check_manuf_name('Apple')
        self.assertTrue(is_valid)
        is_valid = check_manuf_name('Samsung')
        self.assertTrue(is_valid)
        is_valid = check_manuf_name('Google')
        self.assertTrue(is_valid)

    def test_invalid_manufacturer(self):
        '''Returns False: invalid name'''
        is_valid = check_manuf_name('Invalid-Manufacturer')
        self.assertFalse(is_valid)

    def test_invalid_type_int(self):
        '''Returns False: integer'''
        is_valid = check_manuf_name(7)
        self.assertFalse(is_valid)

    def test_invalid_type_bool(self):
        '''Returns False: boolean'''
        is_valid = check_manuf_name(False)
        self.assertFalse(is_valid)
        is_valid = check_manuf_name(True)
        self.assertFalse(is_valid)

    def test_invalid_type_none(self):
        '''Returns False: nonetype'''
        is_valid = check_manuf_name(None)
        self.assertFalse(is_valid)

    def test_invalid_type_no_args(self):
        '''Returns False: no args'''
        is_valid = check_manuf_name(None)
        self.assertFalse(is_valid)

    def tearDown(self):
        db.session.rollback()


class CheckLimitTestCase(TestCase):
    '''check_limit Test Case'''

    def test_valid_limit(self):
        '''Returns True: valid limit'''
        is_valid = check_limit('17')
        self.assertTrue(is_valid)

    def test_invalid_limit(self):
        '''Returns False: invalid limit'''
        is_valid = check_limit('NaN')
        self.assertFalse(is_valid)

    def test_invalid_type_int(self):
        '''Returns False: valid limit of type int'''
        # The func is specifically for checking string conversion
        is_valid = check_limit(21)
        self.assertFalse(is_valid)

    def test_invalid_type_bool(self):
        '''Returns False: boolean'''
        is_valid = check_limit(True)
        self.assertFalse(is_valid)
        is_valid = check_limit(False)
        self.assertFalse(is_valid)

    def test_invalid_type_none(self):
        '''Returns False: nonetype'''
        is_valid = check_limit(None)
        self.assertFalse(is_valid)

    def test_invalid_type_no_args(self):
        '''Returns False: no args'''
        is_valid = check_limit()
        self.assertFalse(is_valid)
