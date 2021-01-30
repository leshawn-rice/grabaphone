from unittest import TestCase
from api.models import APIKey
from app.app import app
from app.database import db

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///grabaphone_test-db'
app.config['SQLALCHEMY_ECHO'] = False


class APIKeyTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

    def test_generate_and_create(self):
        '''Test Generation and Creation of API Key is successful'''
        key = APIKey.generate_and_create()
        self.assertIsInstance(key, APIKey)
        self.assertEqual(key.id, 1)
        self.assertEqual(key, APIKey.query.filter_by(key=key.key).first())
