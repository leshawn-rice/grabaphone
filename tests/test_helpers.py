from unittest import TestCase
from app.app import app
from app.database import db
from api.models import Manufacturer
from api.helpers import check_manuf_name

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
        '''Test valid manufacturer names'''
        is_valid = check_manuf_name('Apple')
        self.assertTrue(is_valid)
        is_valid = check_manuf_name('Samsung')
        self.assertTrue(is_valid)
        is_valid = check_manuf_name('Google')
        self.assertTrue(is_valid)

    def test_invalid_manufacturer(self):
        is_valid = check_manuf_name('Invalid-Manufacturer')
        self.assertFalse(is_valid)

    def tearDown(self):
        db.session.rollback()
