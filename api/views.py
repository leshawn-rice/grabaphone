from flask import render_template, request, jsonify, abort, make_response
from sqlalchemy import func
from app.app import app
from app.database import db
from api.models import APIKey, Manufacturer, Device, Spec
from typing import List
from functools import wraps
import os
import json


MASTERKEY = os.environ.get('MASTER_KEY', 'masterkey')

# TODO
# 3. Add ability to update & delete manufs/devices
# 4. Add UI (almost done)
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
        key = data.get('key')
        if not APIKey.validate(key):
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
        if data.get('master_key') != MASTERKEY:
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
    Creates, saves, and shows the user a unique, 
    random 12-character API key.
    '''
    key = APIKey.generate_and_create()
    return render_template('key_created.html', key=key)

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


# Device Routes
#####################################################################

# Might add additional sorting options later

def get_serialized_devices(manufacturer: str, name: str, limit: str):
    '''
    Gets {limit} devices with the given manufacturer, that match the given name,
    serializes and then returns them
    '''
    limit = int(limit)
    devices = None
    # If 'iPhone' is sent, we want Apple iPhone 12, 11... etc
    if name:
        devices = Device.query.filter(Device.name.ilike(
            r"%{}%".format(name))).limit(limit).all()
    else:
        devices = Device.query.limit(limit).all()
    if manufacturer:
        return [d.serialize() for d in devices if p.manufacturer.name.lower() == manufacturer.lower()]
    return [d.serialize() for d in devices]


def is_manuf_name_valid(name):
    '''
    Checks if the given name matches the name
    of any manufacturers in the DB
    '''
    manuf = Manufacturer.query.filter_by(name=name).first()
    if manuf:
        return True
    return False


@app.route('/api/get-devices', methods=['GET'])
@api_key_required
def get_devices():
    '''
    Get devices
    '''
    data = request.args
    manufacturer = data.get('manufacturer')
    name = data.get('name')
    limit = data.get('limit')

    if not limit:
        limit = 100
    if not is_limit_convertable(limit):
        return (jsonify({'message': f'Limit {limit} invalid!'}), 400)
    if manufacturer and not is_manuf_name_valid(name=manufacturer):
        return (jsonify({'message': f'Manufacturer {manufacturer} invalid!'}), 400)
    else:
        devices = get_serialized_devices(
            manufacturer=manufacturer, name=name, limit=limit)
        return (jsonify({'Devices': devices}), 200)

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


# Device Routes
#####################################################################

def convert_manuf_id(id: str = None):
    try:
        id = int(id)
    except TypeError:
        id = None
    return id


# To seed the db, get device data for each manufacturer, then create devices

@app.route('/api/get-device-data', methods=['GET'])
@api_key_required
@master_key_required
def get_raw_device_data():
    data = request.args
    name = data.get('name')
    if not name:
        return (jsonify({'message': 'You must proved a manufacturers name!'}), 400)

    manuf = Manufacturer.query.filter(Manufacturer.name.ilike(name)).first()

    if not manuf:
        return (jsonify({'message': 'Invalid Manufacturer Name'}), 400)

    devices = {}
    devices[manuf.name] = manuf.scrape_devices()

    return (jsonify(devices), 200)


@app.route('/api/add-specs/<int:id>', methods=['POST'])
@api_key_required
@master_key_required
def add_specs(id):
    data = request.json
    device = Device.query.get(id)

    if not device:
        return (jsonify({'message': f'Device ID {id} invalid!'}), 400)

    specs = device.scrape_specs()

    return (jsonify({'Device': device.serialize()}), 200)


@app.route('/api/add-device', methods=['POST'])
@api_key_required
@master_key_required
def add_device():
    data = request.json

    name = data.get('name')
    url = data.get('url')
    manuf_id = data.get('manuf_id')

    if not name or not url or not manuf_id:
        return (jsonify({'message': 'Invalid Data!'}), 400)

    manuf_id = convert_manuf_id(manuf_id)
    manuf = Manufacturer.query.get(manuf_id)

    if manuf:
        device = Device.create(name=name, manufacturer_id=manuf_id, url=url)
        return (jsonify({'Device': device.serialize()}))
    else:
        return (jsonify({'message': 'Invalid Manufacturer ID!'}), 200)


@app.route('/api/update-devices', methods=['PATCH'])
@api_key_required
@master_key_required
def update_devices():
    pass


@app.route('/api/delete-devices', methods=['DELETE'])
@api_key_required
@master_key_required
def delete_devices():
    pass

#####################################################################
