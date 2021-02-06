import requests
import os
from bs4 import BeautifulSoup as bsoup
from typing import List
from datetime import datetime, date
from app.database import db
from api.helpers import convert_to_date, make_date_valid


###################
#  API Key Model  #
###################


#####################################################################

class APIKey(db.Model):
    '''API Key Model'''
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(12), unique=True, nullable=False)

    def __repr__(self):
        return f'<APIKey #{self.id}: {self.key}>'

    @classmethod
    def validate(cls, key: str):
        if not cls.query.filter_by(key=key).first():
            return False
        return True

    # Considering removing this altogether and just adding the key when user clicks generate
    @classmethod
    def create(cls, key: str):
        '''Creates a new API Key with value key'''
        new_key = cls(key=key)
        db.session.add(new_key)
        db.session.commit()
        return new_key

    @classmethod
    def generate(cls):
        '''
        Creates a unique, random 12-character
        key, and returns it
        '''
        key_created = False
        key = None
        # It's possible to generate an already existing key, this loops until a unique key is created
        while not key_created:
            # The result from os.urandom(x) when hexed is twice the length as the val passed in
            random_key = os.urandom(6).hex()
            if not cls.query.filter_by(key=random_key).first():
                key_created = True
                key = random_key
        return key

    @classmethod
    def generate_and_create(cls):
        '''Generates and creates a new API Key'''
        key = cls.generate()
        return cls.create(key)

#####################################################################


########################
#  Manufacturer Model  #
########################


#####################################################################

class Manufacturer(db.Model):
    '''Manufacturer Model'''
    __tablename__ = 'manufacturers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)

    devices = db.relationship('Device')

    def __repr__(self):
        return f'<Manufacturer #{self.id}: {self.name}>'

    def serialize(self):
        '''
        Returns a dictionary with the manufacturer's
        information, and a list of their devices, for converting
        to JSON
        '''
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,

            'Devices': [p.serialize() for p in self.devices]
        }

    def scrape_devices(self):
        '''
        Scrapes 5 pages of devices by the current manufacturer
        instance from phonearena.com, and returns a list of
        dicts with the device name, url, and manuf id
        '''
        raw_devices = []
        devices = []
        url = self.url

        # The first 5 pages is most recent 180 devices
        for i in range(5):
            response = requests.get(url)
            if response.status_code != 200:
                print(f'Page {i} not found!')
                break
            container = bsoup(response.text, 'html.parser').find(
                id='finder-results')
            current_devices = container.find_all('div', class_='stream-item')
            raw_devices = list(set(raw_devices).union(current_devices))
            url = self.url + f'/page/{i+1}'

        for device in raw_devices:
            name = device.find('p', class_='title').text
            url = device.a['href']
            devices.append({'name': name, 'url': url, 'manuf_id': self.id})

        return devices

    @classmethod
    def get(cls, manufacturer: str = None, limit: int = 100):
        '''
        Gets the manufacturers with the given name and/or all up
        to the limit (defaults to 100) and returns them
        '''
        if limit > 100:
            limit = 100

        manufs = None
        if manufacturer:
            manufs = cls.query.filter_by(name=manufacturer).limit(limit).all()
        else:
            manufs = cls.query.limit(limit).all()
        serialized_manufs = [m.serialize() for m in manufs]
        return serialized_manufs

    @classmethod
    def create(cls, name: str, url: str) -> 'Manufacturer':
        '''Create a new manufacturer'''
        new_manuf = cls(name=name, url=url)
        db.session.add(new_manuf)
        db.session.commit()
        return new_manuf

    @classmethod
    def scrape_all_manufacturer_info(cls):
        '''
        Sends a GET request to phonearena.com/manufacturers
        and returns a list of all the names of the manufacturers
        '''
        info = []
        url = 'https://www.phonearena.com/phones/manufacturers'
        response = requests.get(url)
        page = bsoup(response.text, 'html.parser')
        divs = page.find_all('div', class_='manufacturer-item')

        for manuf in divs:
            info.append({'name': manuf.span.text, 'url': manuf.a['href']})
        return info

    @classmethod
    def create_all(cls):
        '''
        Creates a new Manufacturer for every manufacturer
        on phonearena.com
        '''
        manuf_info = cls.scrape_all_manufacturer_info()
        for manuf in manuf_info:
            name = manuf['name']
            url = manuf['url']
            cls.create(name=name, url=url)

#####################################################################


##################
#  Device Model  #
##################


#####################################################################

class Device(db.Model):
    '''Device Model'''
    __tablename__ = 'devices'

    # Add release date, as date
    # Because we gotta query this dumbass fucking bullshit
    # and i wanna kms

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey(
        'manufacturers.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)
    release_date = db.Column(db.Text)
    image = db.Column(db.Text)
    url = db.Column(db.Text, nullable=False)

    manufacturer = db.relationship('Manufacturer')
    specs = db.relationship('Spec')

    def __repr__(self):
        return f'<Device #{self.id}: {self.manufacturer} {self.name}>'

    def serialize_specs(self):
        '''
        Returns a dictionary with the device's spec
        information, for converting to JSON
        '''
        categories = {}
        for spec in self.specs:
            if spec.category not in categories:
                categories[spec.category] = []

        for spec in self.specs:
            categories[spec.category].append(spec.serialize())

        return categories

    def serialize(self):
        '''
        Returns a dictionary with the device's information,
        and a dict of their specs, for converting to JSON
        '''
        return {
            'id': self.id,
            'manufacturer': self.manufacturer.name,
            'name': self.name,
            'rating': self.rating,
            'release_date': self.release_date,
            'image_url': self.image,
            'device_url': self.url,

            'specs': self.serialize_specs()
        }

    def get_rating(self, page):
        '''
        Gets the user rating for a device off the given
        page if available
        '''
        # recently added
        raw_rating = None
        try:
            raw_rating = page.find('a', class_='widgetRating__phonearena').find(
                'div', class_='score').find_all(text=True, recursive=False)
        except AttributeError:
            try:
                raw_rating = page.find('a', class_='widgetRating__user').find(
                    'div', class_='score').find_all(text=True, recursive=False)
            except AttributeError:
                raw_rating = [0.0]
        rating = " ".join(str(raw_rating[0]).split())
        try:
            self.rating = float(rating)
        except ValueError:
            self.rating = 0.0
        return

    def get_image(self, page):
        '''
        Gets the device image for a device off the given
        page if available
        '''
        try:
            img = page.find('picture', class_='portrait').find(
                'noscript').find('img')
            img_link = img.attrs['src']
            self.image = img_link
        except AttributeError:
            print('No Image Found!')
        return

    def scrape_specs(self) -> List['Spec']:
        '''
        Scrapes all the specs for a device from the 
        device page and creates the specs for the device
        '''
        response = requests.get(self.url)
        # recently added
        page = bsoup(response.text, 'html.parser')
        if not page:
            return []
        self.get_rating(page)
        self.get_image(page)
        try:
            divs = page.find('div', class_='widgetSpecs').find_all('section')
        except AttributeError:
            return []

        specs = []

        for spec_group in divs:
            category = " ".join(str(spec_group.h3.text).split())
            specs_ = spec_group.tbody.find_all('tr')
            for spec in specs_:
                name = " ".join(str(spec.th.text).split())
                description = " ".join(str(spec.td.text).split())
                if 'Availability' in category:
                    if not self.release_date or not len(self.release_date) > 4:
                        # This should make sorting by release date 1000x easier
                        valid_date = make_date_valid(description)
                        self.release_date = valid_date
                        print(f'{self.name} Released: {self.release_date}')
                else:
                    new_spec = Spec.create(
                        device_id=self.id, category=category, name=name, description=description)
                    specs.append(new_spec)
        return specs

    @classmethod
    def get_latest(cls, manufacturer, name, is_released: bool = False):
        '''
        Gets 100 latest devices with the given manufacturer, that match the given name,
        serializes and then returns them
        '''
        devices = None
        if name:
            devices = cls.query.filter(Device.name.ilike(
                r"%{}%".format(name))).all()
        else:
            devices = cls.query.all()

        if manufacturer:
            devices = [
                device for device in devices if device.manufacturer.name.lower() == manufacturer.lower()
            ]

        device_dates = [
            (device, convert_to_date(device.release_date)) for device in devices
        ]
        # Sort devices by latest
        device_dates.sort(key=lambda device: device[1])
        if is_released:
            device_dates.sort(key=lambda device: device[1] < date.today())
        device_dates.reverse()

        return [device[0].serialize() for device in device_dates[0:100]]

    @classmethod
    def get(cls, manufacturer: str, name: str, limit: int = 100):
        '''
        Gets {limit} devices with the given manufacturer, that match the given name,
        serializes and then returns them
        '''
        if limit > 100:
            limit = 100
        devices = None
        # If 'iPhone' is sent, we want Apple iPhone 12, 11... etc
        if name:
            devices = cls.query.filter(Device.name.ilike(
                r"%{}%".format(name))).limit(limit).all()
        else:
            devices = cls.query.limit(limit).all()
        if manufacturer:
            return [device.serialize() for device in devices if device.manufacturer.name.lower() == manufacturer.lower()]
        return [device.serialize() for device in devices]

    @classmethod
    def create(cls, name: str, manufacturer_id: int, url: str) -> 'Device':
        device = cls(manufacturer_id=manufacturer_id, name=name, url=url)
        db.session.add(device)
        db.session.commit()
        return device

#####################################################################


#########################
#  Specification Model  #
#########################


#####################################################################

class Spec(db.Model):
    '''Specification Model'''
    __tablename__ = 'specs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.Integer, db.ForeignKey(
        'devices.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)

    device = db.relationship('Device')

    def __repr__(self):
        return f'<Spec #{self.id}: {self.device.name} - {self.name}: {self.description}>'

    def serialize(self):
        return {
            'name': self.name,
            'description': self.description
        }

    def convert_date(self):
        raw_date = datetime.strptime(self.description, '%B %d, %Y')
        date = raw_date.date()
        self.description = date

    @classmethod
    def create(cls, device_id: int, category: str, name: str, description: str) -> 'Spec':
        new_spec = cls(device_id=device_id, category=category,
                       name=name, description=description)
        db.session.add(new_spec)
        db.session.commit()
        return new_spec

#####################################################################
