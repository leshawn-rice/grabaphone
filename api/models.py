import requests
import os
from bs4 import BeautifulSoup as bsoup
from typing import Set
from app.database import db


class APIKey(db.Model):
    '''API Key Model'''
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(12), unique=True, nullable=False)

    def __repr__(self):
        return f'<APIKey #{self.id}: {self.key}>'

    @classmethod
    def validate(cls, data: dict):
        # Need to see if this is redundant with the data.get(key)
        if 'key' not in data:
            return False

        key = data.get('key')
        if not cls.query.filter_by(key=key).first():
            return False
        return True

    # Considering removing this altogether and just adding the key when user clicks generate
    @classmethod
    def create(cls, key: str):
        '''Creates a new API Key with value key'''
        new_key = cls(key=key)
        db.session.add(new_key)
        db.session.commit(new_key)
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


class Manufacturer(db.Model):
    '''Manufacturer Model'''
    __tablename__ = 'manufacturers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)

    phones = db.relationship('Phone')

    def __repr__(self):
        return f'<Manufacturer #{self.id}: {self.name}>'

    def serialize(self):
        '''
        Returns a dictionary with the manufacturer's
        information, and a list of their phones, for converting
        to JSON
        '''
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,

            'phones': [p.serialize() for p in self.phones]
        }

    def get_phones(self):
        response = requests.get(self.url)
        page = bsoup(response.text, 'html.parser')
        results = page.find(id='finder-results')
        phones = results.find_all('div', class_='stream-item')
        for phone in phones:
            name = phone.find('p', class_='title').text
            url = phone.a['href']
            new_phone = Phone.create(
                name=name, url=url, manufacturer_id=self.id)

    @classmethod
    def create(cls, name: str, url: str) -> 'Manufacturer':
        '''Create a new manufacturer'''
        new_manuf = cls(name=name, url=url)
        db.session.add(new_manuf)
        db.session.commit()
        return new_manuf

    @classmethod
    def get_all_manufacturer_info(cls):
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
        manuf_info = cls.get_all_manufacturer_info()
        for manuf in manuf_info:
            name = manuf['name']
            url = manuf['url']
            cls.create(name=name, url=url)


class Phone(db.Model):
    '''Phone Model'''
    __tablename__ = 'phones'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey(
        'manufacturers.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)

    manufacturer = db.relationship('Manufacturer')
    specs = db.relationship('Spec')

    def __repr__(self):
        return f'<Phone #{self.id}: {self.manufacturer} {self.name}>'

    def serialize_specs(self):
        '''
        Returns a dictionary with the phone's spec
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
        Returns a dictionary with the phone's information, 
        and a dict of their specs, for converting to JSON
        '''
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,

            'specs': self.serialize_specs()
        }

    def get_specs(self) -> Set['Spec']:
        '''

        '''
        response = requests.get(self.url)
        page = bsoup(response.text, 'html.parser')
        divs = page.find('div', class_='widgetSpecs').find_all('section')

        specs = set()

        for spec_group in divs:
            category = " ".join(str(spec_group.h3.text).split())
            specs_ = spec_group.tbody.find_all('tr')
            for spec in specs_:
                name = " ".join(str(spec.th.text).split())
                description = " ".join(str(spec.td.text).split())
                new_spec = Spec.create(
                    phone_id=self.id, category=category, name=name, description=description)
                specs.add(new_spec)
        return specs

    @classmethod
    def create(cls, name: str, manufacturer_id: int, url: str) -> 'Phone':
        new_phone = cls(manufacturer_id=manufacturer_id, name=name, url=url)
        db.session.add(new_phone)
        db.session.commit()
        return new_phone


class Spec(db.Model):
    '''Specification Model'''
    __tablename__ = 'specs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_id = db.Column(db.Integer, db.ForeignKey(
        'phones.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)

    phone = db.relationship('Phone')

    def __repr__(self):
        return f'<Spec #{self.id}: {self.phone.name} - {self.name}: {self.description}>'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    @classmethod
    def create(cls, phone_id: int, category: str, name: str, description: str) -> 'Spec':
        new_spec = cls(phone_id=phone_id, category=category,
                       name=name, description=description)
        db.session.add(new_spec)
        db.session.commit()
        return new_spec
