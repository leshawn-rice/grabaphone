from flask import render_template, request, jsonify, abort, make_response
from app.app import app
from app.database import db
from api.config import MASTER_KEY
# Consider using db.model.ModelName instead of importing models
from api.models import APIKey, Manufacturer, Device, Spec
from api.helpers import convert_manuf_id, validate_json, handle_json
from functools import wraps


# TODO
# 1. Add offset to routes
# 2. Ensure release_date of type Date works
# 3. Finish tests
# 4. Document thoroughly
# 5. Deploy

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
            json_response = jsonify(
                {'message': 'API Key invalid!', 'status': 401})
            response = make_response(json_response, 401)
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
        if data.get('master_key') != MASTER_KEY:
            json_response = jsonify(
                {'message': 'Master Key invalid!', 'status': 401})
            response = make_response(json_response, 401)
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
    json_data = validate_json(
        request.args, ['manufacturer', 'offset', 'limit'])
    json_data = handle_json(json_data)

    manufacturer = json_data['manufacturer']
    offset = json_data['offset']
    limit = json_data['limit']

    manufacturers = Manufacturer.get(
        manufacturer=manufacturer, offset=offset, limit=limit)
    serialized_manufacturers = [manuf.serialize() for manuf in manufacturers]
    response = jsonify({'Manufacturers': serialized_manufacturers})
    return (response, 200)

#####################################################################


# Device Routes
#####################################################################

@app.route('/api/get-latest-devices')
@api_key_required
def get_latest_devices():
    '''
    Get latest devices
    '''
    json_data = validate_json(request.args, ['manufacturer',
                                             'name', 'limit', 'is_released'])
    json_data = handle_json(json_data)

    manufacturer = json_data['manufacturer']
    name = json_data['name']
    limit = json_data['limit']
    is_released = json_data['is_released']

    devices = Device.get_latest(
        manufacturer=manufacturer, name=name, limit=limit, is_released=is_released)
    serialized_devices = [device.serialize() for device in devices]
    response = jsonify({'Devices': serialized_devices})
    return (response, 200)


@app.route('/api/get-devices', methods=['GET'])
@api_key_required
def get_devices():
    '''
    Get devices
    '''
    json_data = validate_json(request.args, ['manufacturer', 'name', 'limit'])
    json_data = handle_json(json_data)

    manufacturer = json_data['manufacturer']
    name = json_data['name']
    limit = json_data['limit']

    devices = Device.get(manufacturer=manufacturer, name=name, limit=limit)
    serialized_devices = [device.serialize() for device in devices]
    response = jsonify({'Devices': serialized_devices})
    return (response, 200)

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
    device = Device.query.get(id)

    if not device:
        response = jsonify({'message': f'Device ID {id} invalid!'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 400)

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
