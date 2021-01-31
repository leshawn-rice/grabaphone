from unittest import TestCase
from api.models import APIKey
from app.app import app
from app.database import db

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///grabaphone_test-db'
app.config['SQLALCHEMY_ECHO'] = False


class APIKeyTestCase(TestCase):
    '''APIKey Test Case'''
    def setUpClass():
        db.drop_all()
        db.create_all()

    def test_validate(self):
        '''Test validation of valid key'''
        key_object = APIKey.generate_and_create()
        key = key_object.key
        is_validated = APIKey.validate(key)
        self.assertTrue(is_validated)

    def test_fail_validate(self):
        '''Test validation of invalid key'''
        key = 'key'
        is_validated = APIKey.validate(key)
        self.assertFalse(is_validated)

    def test_generate(self):
        '''Test Generation of 12-character hexadecimal API Key is successful'''
        print('Starting test')
        key = APIKey.generate()
        print('Key generated')
        self.assertEqual(len(key), 12)
        self.assertIsInstance(key, str)
        self.assertIsNone(APIKey.query.filter_by(key=key).first())

    def test_create(self):
        '''Test Creation of API Key in db is successful'''
        raw_key = '12456abcdef'
        key = APIKey.create(raw_key)
        self.assertIsInstance(key, APIKey)
        self.assertIsInstance(key.id, int)
        self.assertEqual(key, APIKey.query.filter_by(key=key.key).first())

    def test_generate_and_create(self):
        '''Test Generation and Creation of API Key is successful'''
        key = APIKey.generate_and_create()
        self.assertIsInstance(key, APIKey)
        self.assertIsInstance(key.id, int)
        self.assertEqual(key, APIKey.query.filter_by(key=key.key).first())


class DeviceTestCase(TestCase):
    '''Device Test Case'''

    def setUpClass():
        db.drop_all()
        db.create_all()
