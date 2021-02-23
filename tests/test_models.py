from unittest import TestCase
from api.models import APIKey, Device, Manufacturer
from app.app import app
from app.database import db

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///grabaphone_test-db'
app.config['SQLALCHEMY_ECHO'] = False


def add_to_db(item):
    db.session.add(item)
    db.session.commit()


class APIKeyTestCase(TestCase):
    '''APIKey Test Case'''

    @classmethod
    def setUpClass(cls):
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
        db.drop_all()
        db.create_all()

    # Test scraping? Cant be done with test data has to be done with real data

    def setUp(self):
        self.manuf = Manufacturer(
            name='test manuf', url='https://testmanuf.com')
        add_to_db(self.manuf)

    def test_creation(self):
        '''Test that creating a new Device is as expected'''
        device = Device.create(
            name='test device', url='https://testphone.com', manufacturer_id=1)
        self.assertIsInstance(device, Device)
        self.assertEqual(device.name, 'test device')
        self.assertEqual(device.manufacturer, self.manuf)

    def test_serialize(self):
        '''Test that serializing a Device runs correctly'''
        device = Device(name='test device',
                        url='https://testphone.com', manufacturer_id=self.manuf.id)
        add_to_db(device)

        serialized = device.serialize()
        self.assertEqual(serialized, {
            'id': self.manuf.id,
            'manufacturer': 'test manuf',
            'name': 'test device',
            'release_date': None,
            'rating': None,
            'device_url': 'https://testphone.com',
            'image_url': None,
            'specs': {}
        })

    def tearDown(self):
        db.session.rollback()
