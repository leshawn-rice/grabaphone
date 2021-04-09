from app.app import app
from app.database import db
from api.models import Manufacturer, Device
import datetime

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///grabaphone_test'
app.config['SQLALCHEMY_ECHO'] = False


def seed_db():
    db.drop_all()
    db.create_all()
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
            'url': 'https://www.phonearena.com/phones/Apple-iPhone-12_id11417',
            'release_date': None
        },
        {
            'name': 'Galaxy S21 Ultra',
            'manufacturer_id': '2',
            'url': 'https://samsung.com/galaxy-21-ultra',
            'release_date': datetime.date.today()
        },
        {
            'name': 'Pixel 5',
            'manufacturer_id': '3',
            'url': 'https://google.com/pixel-5',
            'release_date': None
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
            url=device['url'],
            release_date=device['release_date']
        )
        db.session.add(dev)
        db.session.commit()
