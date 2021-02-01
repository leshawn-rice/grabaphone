from unittest import TestCase
from api.models import APIKey, Device, Manufacturer
from app.app import app
from app.database import db

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///grabaphone_test-db'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class APIKeyTestCase(TestCase):
    '''APIKey Test Case'''

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
        key = APIKey.generate()
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

    # Test scraping? Cant be done with test data has to be done with real data

    def setUp(self):
        self.manuf = Manufacturer.create(
            name='test manuf', url='https://testmanuf.com')

    def test_creation(self):
        '''Test that creating a new Device is as expected'''
        device = Device.create(
            name='test device', url='https://testphone.com', manufacturer_id=1)
        self.assertIsInstance(device, Device)
        self.assertEqual(device.name, 'test device')
        self.assertEqual(device.manufacturer, self.manuf)

    def test_serialize(self):
        '''Test that serializing a Device runs correctly'''
        device = Device.create(
            name='test device', url='https://testphone.com', manufacturer_id=1)
        serialized = self.device.serialize()
        self.assertEqual(serialized['name'], 'test device')
        self.assertEqual(serialized['rating'], None)
        self.assertEqual(serialized['image_url'], None)
        self.assertEqual(serialized['device_url'], 'https://testphone.com')
        self.assertEqual(serialized['specs'], {})
