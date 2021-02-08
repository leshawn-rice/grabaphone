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

    if manufacturer and not check_manuf_name(name=manufacturer):
        return (jsonify({'message': f'Manufacturer name {manufacturer} invalid!'}), 400)
    if not limit:
        limit = 100
    if not check_limit(limit):
        return (jsonify({'message': f'Limit {limit} invalid!'}), 400)
    limit = int(limit)
    manufacturers = Manufacturer.get(manufacturer=manufacturer, limit=limit)
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
    if not check_limit(limit):
        return (jsonify({'message': f'Limit {limit} invalid!'}), 400)
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
        return (jsonify({'Manufacturers': [m.serialize() for m in Manufacturer.query.all()]}), 200)
    else:
        return (jsonify({'message': 'Error adding manufacturers!'}), 400)

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
        return (jsonify({'message': 'You must proved a manufacturers name!'}), 400)

    manuf = Manufacturer.query.filter(Manufacturer.name.ilike(name)).first()

    if not manuf:
        return (jsonify({'message': 'Invalid Manufacturer Name'}), 400)

    devices = {}
    devices['id'] = manuf.id
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

    db.session.commit()

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

#####################################################################
