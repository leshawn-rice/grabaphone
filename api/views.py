from flask import render_template, request, jsonify
from sqlalchemy import func
from app.app import app
from app.database import db
from api.models import APIKey, Manufacturer, Phone
from typing import List
import os


####################
#  No auth Routes  #
####################

# API Key Generation
#####################################################################
@app.route('/generate-api-key', methods=['GET', 'POST'])
def generate_api_key():
    '''
    If the user sent a form (save key),
    save the api key in the db. Otherwise,
    show the user a unique, random 12-character
    key, along with a form to save they key.
    '''
    raw_key = APIKey.generate()
    key_in_db = APIKey.create(raw_key)
    return render_template('key_created.html', key=key_in_db)

#####################################################################

#################
#  User Routes  #
#################

# Manufacturer Routes
#####################################################################


def is_limit_convertable(limit: str = None):
    '''
    Takes a string value for limit,
    checks if it can be converted to an integer,
    and returns True/False based on that
    '''
    try:
        limit = int(limit)
        return True
    except TypeError:
        return False


def get_serialized_manufs(name: str = None, limit: str = '100') -> List['Manufacturer']:
    '''
    Takes in an optional name and limit, and returns a list of serialized
    manufacturers matching the name and/or limit.
    '''
    limit = int(limit)
    manufs = None
    # We need this if statement because if name is None and we filter by it we get 0 results
    if name:
        manufs = Manufacturer.query.filter_by(name=name).limit(limit).all()
    else:
        manufs = Manufacturer.query.limit(limit).all()
    # Put manufacturers in JSON format
    serialized_manufs = [m.serialize() for m in manufs]
    return serialized_manufs


# Name, limit, offset, rating ** (Still need to come up with a pythonic way to rate the manufs)
@app.route('/api/get-manufacturers', methods=['GET'])
def get_manufacturers():
    '''Get manufacturers'''
    data = request.args
    name = data.get('name')
    limit = data.get('limit')

    if not APIKey.validate(data):
        return (jsonify({'message': 'API Key validation failed!'}), 200)
    if not limit:
        limit = 100
    if not is_limit_convertable(limit):
        return (jsonify({'message': f'Limit {limit} invalid!'}), 200)
    else:
        serialized_manufs = get_serialized_manufs(name=name, limit=limit)
        return (jsonify({'Manufacturers': serialized_manufs}), 200)

#####################################################################


# Phone Routes
#####################################################################

@app.route('/api/get-phones', methods=['GET'])
def get_phones():
    # Need to come up with a way to sort by battery, camera etc.
    pass

#####################################################################

######################
#  Webmaster Routes  #
######################


def validate_master_key(data):
    if 'master_key' not in data:
        return False
    master_key = data.get('master_key')
    # Obvi change this in prod
    if master_key != 'masterkey':
        return False
    return True

# Manufacturer Routes
#####################################################################


@app.route('/api/add-manufacturers', methods=['POST'])
def add_manufacturers():
    data = request.json
    if not APIKey.validate(data) or not validate_master_key(data):
        print('Key Issue!')
        return (jsonify({'message': 'Key Validation Failed!'}), 200)

    Manufacturer.create_all()

    if Manufacturer.query.all():
        return (jsonify({'message': 'Success'}), 200)
    else:
        return (jsonify({'message': 'Error'}), 200)


@app.route('/api/update-manufacturers', methods=['PATCH'])
def update_manufacturers():
    pass


@app.route('/api/delete-manufacturers', methods=['DELETE'])
def delete_manufacturers():
    pass

#####################################################################


# Phone Routes
#####################################################################

def convert_manuf_id(id: str = None):
    try:
        id = int(id)
    except TypeError:
        id = None
    return id


# To seed the db, get phone data for each manufacturer, then create phones

@app.route('/api/get-phone-data', methods=['GET'])
def get_raw_phone_data():
    data = request.args
    name = data.get('name')
    if not APIKey.validate(data) or not validate_master_key(data):
        return (jsonify({'message': 'Key Validation Failed!'}), 400)

    manuf = Manufacturer.query.filter(func.lower(
        Manufacturer.name) == name.lower()).first()

    if not manuf:
        return (jsonify({'message': 'Invalid Manufacturer Name'}), 400)

    phones = {}
    phones[manuf.name] = manuf.scrape_phones()

    return (jsonify(phones), 200)


@app.route('/api/add-specs/<int:phone_id>', methods=['POST'])
def add_specs(phone_id):
    data = request.json
    if not APIKey.validate(data) or not validate_master_key(data):
        return (jsonify({'message': 'Key Validation Failed!'}), 200)

    phone = Phone.query.get(phone_id)

    if not phone:
        return (jsonify({'message': f'Phone ID {phone_id} invalid!'}), 200)

    specs = phone.scrape_specs()

    return (jsonify({'Phone': phone.serialize()}), 200)


@app.route('/api/add-phone', methods=['POST'])
def add_phone():
    data = request.json

    name = data.get('name')
    url = data.get('url')
    manuf_id = data.get('manuf_id')

    if not APIKey.validate(data) or not validate_master_key(data):
        return (jsonify({'message': 'Key Validation Failed!'}), 200)
    if not name or not url or not manuf_id:
        return (jsonify({'message': 'Invalid Data!'}), 200)

    manuf_id = convert_manuf_id(manuf_id)
    manuf = Manufacturer.query.get(manuf_id)

    if manuf:
        phone = Phone.create(name=name, manufacturer_id=manuf_id, url=url)
        return (jsonify({'Phone': phone.serialize()}))
    else:
        return (jsonify({'message': 'Invalid Manufacturer ID!'}), 200)


@app.route('/api/update-phones', methods=['PATCH'])
def update_phones():
    pass


@app.route('/api/delete-phones', methods=['DELETE'])
def delete_phones():
    pass

#####################################################################
