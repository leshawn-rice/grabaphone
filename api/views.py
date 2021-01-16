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
@app.route('/generate-api-key', methods=['GET', 'POST'])
def generate_api_key():
    '''
    If the user sent a form (save key),
    save the api key in the db. Otherwise,
    show the user a unique, random 12-character
    key, along with a form to save they key.
    '''
    if request.method == 'POST':
        key = request.form.get('key')
        if key:
            added_key = APIKey.create(key)
            return render_template('key_created.html', key=added_key)
    else:
        key = APIKey.generate()
        return render_template('generate_api_key.html', key=key)

#####################################################################

#################
#  User Routes  #
#################

# Manufacturer Routes
#####################################################################


def validate_limit(limit):
    try:
        limit = int(limit)
        return True
    except ValueError:
        return False


# Name, limit, offset, rating **
@app.route('/api/get-manufacturers', methods=['GET'])
def get_manufacturers():
    '''Get manufacturers'''
    data = request.args
    if not APIKey.validate(data):
        return (jsonify({'message': 'API Key validation failed!'}), 400)

    name = data.get('name')
    limit = data.get('limit')

    if not validate_limit(limit):
        return (jsonify({'message': f'Limit {limit} invalid!'}), 400)
    else:
        limit = int(limit)
        manufs = Manufacturer.get(name=name, limit=limit)
        return (jsonify({'Manufacturers': manufs}), 200)

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

    if not APIKey.validate(data) or not validate_master_key(data):
        return (jsonify({'message': 'Key Validation Failed!'}), 400)

    manufs = Manufacturer.query.offset(offset).limit(limit).all()

    for manufacturer in manufs:
        manufacturer.scrape_phones()
        for phone in manufacturer.phones:
            phone.scrape_specs()
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
