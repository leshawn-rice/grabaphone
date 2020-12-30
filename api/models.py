import requests
from bs4 import BeautifulSoup as bsoup
from app.database import db


class APIKey(db.Model):
    '''API Key Model'''
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(12), unique=True, nullable=False)

    def __repr__(self):
        return f'<APIKey #{self.id}: {self.key}>'

class Manufacturer(db.Model):
    '''Manufacturer Model'''
    __tablename__ = 'manufacturers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)

    phones = db.relationship('Phone')

    def __repr__(self):
        return f'<Manufacturer #{self.id}: {self.name}>'


    def create_phones(self):
        url = 'https://www.phonearena.com/phones/{self.name}'
        response = requests.get(url)
        page = bsoup(response.text, 'html.parser')
        results = page.find(id='finder-results')
        phones = results.find_all('div', class_='stream-item')
        for phone in phones:
            name = phone.find('p', class_='title').text
            phone_url = phone.a['href']
            new_phone = Phone.create(name=name)
            new_phone.get_specs(url=phone_url)


    @classmethod
    def get_info(cls):
        names = []
        url = 'https://www.phonearena.com/phones/manufacturers'
        response = requests.get(url)
        page = bsoup(response.text, 'html.parser')
        divs = page.find_all('div', class_='manufacturer-item')

        for manuf in divs:
            names.append(manuf.span.text)
        return names


    @classmethod
    def create(cls, name: str) -> Manufacturer:
        '''Create a new manufacturer'''
        new_manuf = cls(name=name)
        db.session.add(new_manuf)
        db.session.commit()
        return new_manuf


    @classmethod
    def create_all(cls):
        names = cls.get_info()
        for name in names:
            cls.create(name=name)




class Phone(db.Model):
    '''Phone Model'''
    __tablename__ = 'phones'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturers.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)

    manufacturer = db.relationship('Manufacturer')
    specs = db.relationship('Spec')


    def __repr__(self):
        return f'<Phone #{self.id}: {self.manufacturer} {self.name}>'


    def get_specs(cls, url: str) -> List[Spec]:
        response = requests.get(url)
        page = bsoup(response.text, 'html.parser')
        specs_div = page.find('div', class_='widgetSpecs').find_all('section')

        for spec_group in specs_div:
            category = str(spec_group.h3.text).strip().strip('\n')
            specs = spec_group.tbody.find_all('tr')
            for spec in specs:
                name = str(spec.th.text).strip().strip('\n')
                description = str(spec.td.text).strip().strip('\n')
                new_spec = Spec.create(phone_id=self.id, category=category, name=name, description=description)


    @classmethod
    def create(cls, name: str, manufacturer_id: int) -> Phone:
        new_phone = cls(manufacturer_id=manufacturer_id, name=name)
        db.session.add(new_phone)
        db.session.commit()
        return new_phone


class Spec(db.Model):
    '''Specification Model'''
    __tablename__ = 'specs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_id = db.Column(db.Integer, db.ForeignKey('phones.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)

    phone = db.relationship('Phone')


    def __repr__(self):
        return f'<Spec #{self.id}: {self.phone.name} - {self.name}: {self.description}>'


    @classmethod
    def create(cls, phone_id: int, category: str, name: str, description: str) -> Spec:
        new_spec = cls(phone_id=phone_id, category=category, name=name, description=description)
        db.session.add(new_spec)
        db.session.commit()
        return new_spec
