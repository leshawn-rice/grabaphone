from flask import render_template, request, jsonify
from app.app import app
from app.database import db
from api.models import APIKey, Manufacturer, Phone
import os


####################
#  No auth Routes  #
####################

# API Key Generation
#####################################################################

def add_key(key):
    '''
    Tries to add the key to the db,
    if the key already exists, show the 
    error message to the user
    '''
    # Try to add the key to the db,
    # if the key exists show error message to user
    try:
        new_key = APIKey(key=key)
        db.session.add(new_key)
        db.session.commit()
        return new_key
    # Get name of error
    except:
        return 'KEY COULD NOT BE SAVED'


def create_key():
    '''
    Creates a unique, random 12-character
    key, and returns it
    '''
    key_created = False
    key = None
    while not key_created:
        # The result from os.urandom(x) when hexed is twice the length as the val passed in
        random_key = os.urandom(6).hex()
        if not APIKey.query.filter_by(key=random_key).first():
            key_created = True
            key = random_key
    return key


@app.route('/generate-api-key', methods=['GET', 'POST'])
def generate_api_key():
    '''
    If the user sent a form (save key),
    save the api key in the db. Otherwise,
    show the user a unique, random 12-character
    key, along a 'form' to save they key.
    '''
    if request.method == 'POST':
        key = request.form.get('key')
        if key:
            added_key = add_key(key)
            return render_template('key_created.html', key=added_key)
    else:
        key = create_key()
        return render_template('generate_api_key.html', key=key)

#####################################################################

#################
#  User Routes  #
#################


def validate_api_key(data):
    if 'key' not in data:
        return False
    request_key = data['key']
    if not APIKey.query.filter_by(key=request_key):
        return False
    return True


# Manufacturer Routes
#####################################################################

def get_manuf_by_name(name: str = None):
    '''
    Gets the first manufacturer with a given namee,
    and returns a serialized dict with the manufacturer's info
    '''
    if name:
        manuf = Manufacturer.query.filter_by(name=name).first()
        if manuf:
            return ({'manufacturers': [manuf.serialize()]}, 200)
        else:
            return ({'manufacturers': []}, 200)
    return ({'message': 'Name cannot be blank!'}, 400)


def get_manuf_by_limit(limit: int = None):
    '''
    Gets the first x manufacturer where x = limi,
    and returns a list of serialized dicts with the manufacturers' info
    '''
    # If limit is None or a type other than int
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return ({'message': f'Invalid param limit: {limit}'}, 400)
        if limit > 100:
            limit = 100
        manufs = Manufacturer.query.limit(limit).all()
        if manufs:
            serialized = [m.serialize() for m in manufs]
            # Add "manufacturers: to this"
            return ({'manufacturers': serialized}, 200)
        else:
            return ({'manufacturers': []}, 200)
    return ({'message': f'Limit cannot be blank!'}, 400)


def get_first_100_manufs():
    '''
    Gets the first 100 manufacturers,
    and returns a list of serialized dicts with the manufacturers' info
    '''
    manufs = Manufacturer.query.limit(100).all()
    if manufs:
        serialized = [m.serialize() for m in manufs]
        return ({'manufacturers': serialized}, 200)
    return ({'manufacturers': []}, 200)


@app.route('/api/get-manufacturers', methods=['GET'])
def get_manufacturers():
    '''Get manufacturers'''
    data = request.args
    if not validate_api_key(data):
        return (jsonify({'message': 'API Key validation failed!'}), 400)
    name = data.get('name')
    limit = data.get('limit')
    result = None
    if name:
        result = get_manuf_by_name(name)
    if limit:
        result = get_manuf_by_limit(limit)
    if not result:
        result = get_first_100_manufs()

    return (jsonify(result[0]), result[1])

#####################################################################


# Phone Routes
#####################################################################

@app.route('/api/get-phones', methods=['GET'])
def get_phones():
    pass

#####################################################################

######################
#  Webmaster Routes  #
######################


def validate_master_key(data):
    if 'master_key' not in data:
        return False
    master_key = data['master_key']
    if master_key != 'masterkey':
        return False
    return True

# Manufacturer Routes
#####################################################################


@app.route('/api/add-manufacturers', methods=['POST'])
def add_manufacturers():
    data = request.json
    is_api_validated = validate_api_key(data)
    is_master_validated = validate_master_key(data)
    if not is_api_validated or not is_master_validated:
        return (jsonify({'message': 'Key Validation Failed!'}), 400)
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

@app.route('/api/add-phones', methods=['POST'])
def add_phones():
    data = request.json
    limit = 1
    offset = 0
    if 'offset' in data:
        offset = data['offset']
    if 'limit' in data:
        limit = data['limit']

    if not validate_api_key(data) or not validate_master_key(data):
        return (jsonify({'message': 'Key Validation Failed!'}), 400)

    manufs = Manufacturer.query.offset(offset).limit(limit).all()

    for manufacturer in manufs:
        manufacturer.get_phones()
        for phone in manufacturer.phones:
            phone.get_specs()
    if Phone.query.all():
        return (jsonify({'message': 'Success'}), 200)
    else:
        return (jsonify({'message': 'Error'}), 200)


@app.route('/api/update-phones', methods=['PATCH'])
def update_phones():
    pass


@app.route('/api/delete-phones', methods=['DELETE'])
def delete_phones():
    pass

#####################################################################
