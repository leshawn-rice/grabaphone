import requests
from bs4 import BeautifulSoup as bsoup

# Get more manufacturer info

# Gonna probably run this one time before deployment, then periodically


class Manufacturer:
    def __init__(self, name: str):
        self.name = name
        self.phones = []

    def add_phone(self, phone_info: dict):
        new_phone = Phone(phone_info)
        self.phones.append(new_phone)


class Phone:
    def __init__(self, info: dict):
        self.name = info.get('Name')
        self.specs = info.get('Specs')


def serialize_manufacturer(manuf):
    manuf_dict = {}
    if not manuf:
        raise ValueError

    manuf_dict[manuf.span.text] = manuf.a['href']
    return manuf_dict


def get_manufacturer_info():
    manufs = []
    url = 'https://www.phonearena.com/phones/manufacturers'
    response = requests.get(url)
    manufs_page = bsoup(response.text, 'html.parser')

    manuf_divs = manufs_page.find_all('div', class_='manufacturer-item')

    for manufacturer in manuf_divs:
        manuf_dict = serialize_manufacturer(manufacturer)
        manufs.append(manuf_dict)

    return manufs


def get_all_phone_info(url):
    phone_info = []
    response = requests.get(url)
    manuf_page = bsoup(response.text, 'html.parser')
    manuf = manuf_page.find(id='finder-results')
    phones = manuf.find_all('div', class_='stream-item')
    for phone in phones:
        phone_dict = {}
        phone_name = phone.find('p', class_='title').text
        phone_link = phone.a['href']
        phone_dict[phone_name] = phone_link
        phone_info.append(phone_dict)

    return phone_info


def get_phone_info(url: str, name: str):
    info = {}
    info['Name'] = name
    info['Specs'] = {}
    response = requests.get(url)
    phone_page = bsoup(response.text, 'html.parser')
    specs = phone_page.find('div', class_='widgetSpecs').find_all('section')

    for spec in specs:
        spec_group = str(spec.h3.text).strip().strip('\n')
        all_specs = spec.tbody.find_all('tr')
        info['Specs'][spec_group] = {}
        for s in all_specs:
            name = str(s.th.text).strip().strip('\n')
            description = str(s.td.text).strip().strip('\n')
            info['Specs'][spec_group][name] = description

    return info


def create_phone(phone: dict):
    phone_name = next(iter(phone.keys()))
    print(f'Collecting {phone_name}...')
    phone_link = next(iter(phone.values()))
    info = get_phone_info(url=phone_link, name=phone_name)
    return info


def create_manufacturers():
    manufacturer_info = get_manufacturer_info()
    manufacturers = []

    for manufacturer in manufacturer_info:
        manuf_name = next(iter(manufacturer.keys()))
        print(f'Collecting {manuf_name}...')
        manuf_link = next(iter(manufacturer.values()))
        manuf = Manufacturer(manuf_name)

        phone_info = get_all_phone_info(manuf_link)

        for phone in phone_info:
            phone_info = create_phone(phone)
            manuf.add_phone(phone_info)

        manufacturers.append(manuf)

        print(f'{manuf_name} Collected!')
        is_finished = input('Want to exit?: (Y) / Anything else: ')
        if is_finished == 'Y' or is_finished == 'y':
            break

    return manufacturers
