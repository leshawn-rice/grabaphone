from app.app import app
from app.database import db
from api.models import Manufacturer, Device

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///grabaphone_test'
app.config['SQLALCHEMY_ECHO'] = False


def seed_db():
    mock_manufs = [
        {
            'name': 'Apple',
            'url': 'https://apple.com'
        },
        {
            'name': 'Samsung',
            'url': 'https://samsung.com'
        },
        {
            'name': 'Google',
            'url': 'https://google.com'
        }
    ]

    mock_devices = [
        {
            'name': 'Apple iPhone 12',
            'manufacturer_id': '1',
            'url': 'https://apple.com/iphone-12'
        },
        {
            'name': 'Galaxy S21 Ultra',
            'manufacturer_id': '2',
            'url': 'https://samsung.com/galaxy-21-ultra'
        },
        {
            'name': 'Pixel 5',
            'manufacturer_id': '3',
            'url': 'https://google.com/pixel-5'
        }
    ]
    for manufacturer in mock_manufs:
        manuf = Manufacturer(
            name=manufacturer['name'],
            url=manufacturer['url']
        )
        db.session.add(manuf)
        db.session.commit()

    for device in mock_devices:
        dev = Device(
            name=device['name'],
            manufacturer_id=device['manufacturer_id'],
            url=device['url']
        )
        db.session.add(dev)
        db.session.commit()
