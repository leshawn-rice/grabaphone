from unittest import TestCase
from api.models import APIKey, Device, Manufacturer
from tests.setup_tests import db, seed_db
import datetime


class APIKeyTestCase(TestCase):
    '''APIKey Test Case'''

    @classmethod
    def setUpClass(cls):
        seed_db()

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

    def tearDown(self):
        db.session.rollback()


class DeviceTestCase(TestCase):
    '''Device Test Case'''

    @classmethod
    def setUpClass(cls):
        seed_db()

    def test_create(self):
        '''Test that creating a new Device is as expected'''
        manufacturer = Manufacturer.query.first()
        device = Device.create(
            name='test device', url='https://testphone.com', manufacturer_id=1)
        self.assertIsInstance(device, Device)
        self.assertEqual(device.name, 'test device')

    def test_serialize(self):
        '''Test that serializing a Device runs correctly'''
        device = Device.create(
            name='test dev', url='https://test.com', manufacturer_id=1)

        serialized = device.serialize()
        self.assertEqual(serialized, {
            'id': device.id,
            'manufacturer': 'Apple',
            'name': 'test dev',
            'release_date': None,
            'rating': None,
            'device_url': 'https://test.com',
            'image_url': None,
            'specs': {}
        })

    def test_get(self):
        '''Test that getting a device runs correctly'''
        devices = Device.get(manufacturer='Apple',
                             name='iPhone', offset=0, limit=1)
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].name, 'Apple iPhone 12')
        self.assertEqual(devices[0].manufacturer.name, 'Apple')
        self.assertEqual(devices[0].rating, None)

    def test_get_latest(self):
        devices = Device.get_latest()
        self.assertEqual(devices[0].name, 'Galaxy S21 Ultra')
        self.assertEqual(devices[0].manufacturer.name, 'Samsung')
        self.assertEqual(devices[0].rating, None)
        self.assertIsInstance(devices[0].release_date, datetime.date)

    def test_scrape_specs(self):
        device = Device.query.get(1)
        device.scrape_specs()
        self.assertIsInstance(device.rating, float)
        # iPhone 12 released Oct 23, 2020
        self.assertEqual(device.release_date, datetime.datetime.strptime(
            'Oct 23, 2020', '%b %d, %Y').date())
        self.assertIsInstance(device.specs, list)

    def tearDown(self):
        db.session.rollback()
