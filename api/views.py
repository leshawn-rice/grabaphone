from flask import render_template, request, jsonify, abort, make_response
from sqlalchemy import func
from app.app import app
from app.database import db
from api.models import APIKey, Manufacturer, Phone, Spec
from typing import List
from functools import wraps
import os
import json


# TODO
# 2. Add get-phones route
# 3. Add ability to update & delete manufs/phones
# 4. Add UI
# 5. Add tests
# 6. Document
# 7. Deploy

#######################
#  Custom Decorators  #
#######################

#####################################################################
# Not sure if abort is the best way to go about sending the error back
def api_key_required(f):
    '''Decorator to validate API Key'''
    @wraps(f)
    def decorated_func(*args, **kwargs):
        data = None
        if request.method == 'GET':
            data = request.args
        else:
            data = request.json
        if not APIKey.validate(data):
            response = make_response(
                jsonify({'message': 'API Key invalid!', 'status': 401}), 401)
            abort(response)
        return f(*args, **kwargs)
    return decorated_func


def master_key_required(f):
    '''Decorator to validate master key (for updating db)'''
    @wraps(f)
    def decorated_func(*args, **kwargs):
        data = None
        if request.method == 'GET':
            data = request.args
        else:
            data = request.json
        print('Validating master')
        print(data.get('master_key'))
        if data.get('master_key') != 'masterkey':
            print(data.get('master_key'))
            response = make_response(
                jsonify({'message': 'Master Key invalid!', 'status': 401}), 401)
            abort(response)
        return f(*args, **kwargs)
    return decorated_func

#####################################################################

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
    except ValueError:
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
@api_key_required
def get_manufacturers():
    '''Get manufacturers'''
    # Add offset
    data = request.args
    name = data.get('name')
    limit = data.get('limit')

    if not limit:
        limit = 100
    if not is_limit_convertable(limit):
        return (jsonify({'message': f'Limit {limit} invalid!'}), 400)
    else:
        serialized_manufs = get_serialized_manufs(name=name, limit=limit)
        return (jsonify({'Manufacturers': serialized_manufs}), 200)

#####################################################################


# Phone Routes
#####################################################################

def sort_phones(sort):
    # Get phones by release date
    a = Spec.query.filter(Spec.category == 'Availability').order_by(
        Spec.description.desc()).all()
    # Get phones by price
    b = Spec.query.filter(Spec.category.ilike(
        'Buyers information'), Spec.name.ilike('Price:')).order_by(Spec.description.desc()).all()

    s = a + b

    phones = []

    for spec in s:
        if spec.phone not in phones:
            phones.append(spec.phone)

    # This is if we only wanna return the phone name and the requested specs
    # for spec in s:
    #     phones[spec.phone.name] = {}

    # for spec in s:
    #     phones[spec.phone.name][spec.name] = spec.description

    # print(phones)

    return phones


def sort_and_get_phones(manufacturer: str, name: str, limit: str, raw_sort: str):
    all_phones = Phone.query.all()
    sort = None
    sorting_map = {
        'release': ('oldest', 'newest'),
        'price': ('highest', 'lowest'),
        'rating': ('highest', 'lowest')
    }

    if manufacturer:
        m = Manufacturer.query.filter(
            Manufacturer.name.ilike(manufacturer)).first()
        if m:
            all_phones = m.phones

    if raw_sort:
        sort = json.loads(raw_sort)

    phones = sort_phones(sort)

    # This is basically what sort_phones() does but a bit different
    # p = Phone.query.join(Spec, Phone.id == Spec.phone_id).add_columns(
    #     Spec.name, Spec.description).filter(Spec.category == 'Availability').order_by(Spec.description.asc()).all()

    # phones = [p[0].serialize() for p in p]

    return [p.serialize() for p in phones]


@app.route('/api/get-phones', methods=['GET'])
@api_key_required
def get_phones():
    # Don't need to come up with a way to sort by battery, camera etc.
    data = request.args
    manufacturer = data.get('manufacturer')
    name = data.get('name')
    limit = data.get('limit')
    sort = data.get('sort')

    if not limit:
        limit = 100
    if not is_limit_convertable(limit):
        return (jsonify({'message': f'Limit {limit} invalid!'}), 400)
    else:
        phones = sort_and_get_phones(
            manufacturer=manufacturer, name=name, limit=limit, raw_sort=sort)
        # return {'message': 'hey'}
        return (jsonify({'Phones': phones}), 200)

#####################################################################

######################
#  Webmaster Routes  #
######################

# Manufacturer Routes
#####################################################################


@app.route('/api/add-manufacturers', methods=['POST'])
@api_key_required
@master_key_required
def add_manufacturers():
    data = request.json
    Manufacturer.create_all()

    if Manufacturer.query.all():
        return (jsonify({'Manufacturers': [m.serialize() for m in Manufacturer.query.all()]}), 200)
    else:
        return (jsonify({'message': 'Error adding manufacturers!'}), 400)


@app.route('/api/update-manufacturers', methods=['PATCH'])
@api_key_required
@master_key_required
def update_manufacturers():
    pass


@app.route('/api/delete-manufacturers', methods=['DELETE'])
@api_key_required
@master_key_required
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
@api_key_required
@master_key_required
def get_raw_phone_data():
    data = request.args
    name = data.get('name')
    manuf = Manufacturer.query.filter(Manufacturer.name.ilike(name)).first()

    if not manuf:
        return (jsonify({'message': 'Invalid Manufacturer Name'}), 400)

    phones = {}
    phones[manuf.name] = manuf.scrape_phones()

    return (jsonify(phones), 200)


@app.route('/api/add-specs/<int:phone_id>', methods=['POST'])
@api_key_required
@master_key_required
def add_specs(phone_id):
    data = request.json
    phone = Phone.query.get(phone_id)

    if not phone:
        return (jsonify({'message': f'Phone ID {phone_id} invalid!'}), 400)

    specs = phone.scrape_specs()

    return (jsonify({'Phone': phone.serialize()}), 200)


@app.route('/api/add-phone', methods=['POST'])
@api_key_required
@master_key_required
def add_phone():
    data = request.json

    name = data.get('name')
    url = data.get('url')
    manuf_id = data.get('manuf_id')

    if not name or not url or not manuf_id:
        return (jsonify({'message': 'Invalid Data!'}), 400)

    manuf_id = convert_manuf_id(manuf_id)
    manuf = Manufacturer.query.get(manuf_id)

    if manuf:
        phone = Phone.create(name=name, manufacturer_id=manuf_id, url=url)
        return (jsonify({'Phone': phone.serialize()}))
    else:
        return (jsonify({'message': 'Invalid Manufacturer ID!'}), 200)


@app.route('/api/update-phones', methods=['PATCH'])
@api_key_required
@master_key_required
def update_phones():
    pass


@app.route('/api/delete-phones', methods=['DELETE'])
@api_key_required
@master_key_required
def delete_phones():
    pass

#####################################################################
