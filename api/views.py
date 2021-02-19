from flask import render_template, request, jsonify, abort, make_response
from app.app import app
from app.database import db
from api.models import APIKey, Manufacturer, Device, Spec
from api.helpers import check_manuf_name, check_limit, convert_manuf_id
from typing import List
from functools import wraps
import os
from datetime import datetime


MASTERKEY = os.environ.get('MASTER_KEY', 'masterkey')

# TODO
# add offset to routes
# 1. Finish UI (almost done)
# 2. Add tests
# 3. Document
# 4. Deploy

#######################
#  Custom Decorators  #
#######################

#####################################################################


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


@app.route('/api/get-manufacturers', methods=['GET'])
@api_key_required
def get_manufacturers():
    '''Get manufacturers'''
    # Add offset
    data = request.args
    manufacturer = data.get('manufacturer')
    limit = data.get('limit')

    print('STARTING GET MANUFS')

    if manufacturer and not check_manuf_name(name=manufacturer):
        return (jsonify({'message': f'Manufacturer name {manufacturer} invalid!'}), 400)
    if not limit:
        limit = 100
    if not check_limit(limit):
        return (jsonify({'message': f'Limit {limit} invalid!'}), 400)
    limit = int(limit)
    print('GETTING MANUFS')
    manufacturers = Manufacturer.get(manufacturer=manufacturer, limit=limit)
    print('RETURNING MANUFS')
    return (jsonify({'Manufacturers': manufacturers}), 200)

#####################################################################


# Device Routes
#####################################################################

@app.route('/api/get-latest-devices')
@api_key_required
def get_latest_devices():
    '''
    Get latest devices
    '''
    data = request.args
    manufacturer = data.get('manufacturer')
    name = data.get('name')
    limit = data.get('limit')
    # Only sent if you want is_released
    is_released = data.get('is_released')
    is_released = bool(is_released)
    if limit and not check_limit(limit):
        return (jsonify({'message': f'Limit {limit} invalid!'}), 400)
    if limit:
        limit = int(limit)
    if manufacturer and not check_manuf_name(name=manufacturer):
        return (jsonify({'message': f'Manufacturer {manufacturer} invalid!'}), 400)
    else:
        devices = Device.get_latest(
            manufacturer=manufacturer, name=name, limit=limit, is_released=is_released)
        return (jsonify({'Devices': devices}), 200)


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
    if not check_limit(limit):
        return (jsonify({'message': f'Limit {limit} invalid!'}), 400)
    limit = int(limit)
    if manufacturer and not check_manuf_name(name=manufacturer):
        return (jsonify({'message': f'Manufacturer {manufacturer} invalid!'}), 400)
    else:
        devices = Device.get(manufacturer=manufacturer, name=name, limit=limit)
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
        response = jsonify(
            {'Manufacturers': [m.serialize() for m in Manufacturer.query.all()]})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 200)
    else:
        response = jsonify({'message': 'Error adding manufacturers!'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 400)


#####################################################################


# Device Routes
#####################################################################


@app.route('/api/get-device-data', methods=['GET'])
@api_key_required
@master_key_required
def get_raw_device_data():
    data = request.args
    name = data.get('name')
    if not name:
        response = jsonify(
            {'message': 'You must proved a manufacturers name!'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 400)

    manuf = Manufacturer.query.filter(Manufacturer.name.ilike(name)).first()

    if not manuf:
        response = jsonify({'message': 'Invalid Manufacturer Name'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 400)

    devices = {}
    devices['id'] = manuf.id
    devices[manuf.name] = manuf.scrape_devices()

    response = jsonify(devices)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return (response, 200)


@app.route('/api/add-specs/<int:id>', methods=['POST'])
@api_key_required
@master_key_required
def add_specs(id):
    data = request.json
    device = Device.query.get(id)

    if not device:
        response = jsonify({'message': f'Device ID {id} invalid!'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 400)

    specs = device.scrape_specs()

    db.session.commit()
    response = jsonify({'Device': device.serialize()})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return (response, 200)


@app.route('/api/add-device', methods=['POST'])
@api_key_required
@master_key_required
def add_device():
    data = request.json

    name = data.get('name')
    url = data.get('url')
    manuf_id = data.get('manuf_id')

    if not name or not url or not manuf_id:
        response = jsonify({'message': 'Invalid Data!'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 400)

    manuf_id = convert_manuf_id(manuf_id)
    manuf = Manufacturer.query.get(manuf_id)

    if manuf:
        device = Device.create(name=name, manufacturer_id=manuf_id, url=url)
        response = jsonify({'Device': device.serialize()})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 200)
    else:
        response = jsonify({'message': 'Invalid Manufacturer ID!'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 200)

#####################################################################
