from flask import render_template, request, jsonify
from app.app import app
from app.database import db
from api.models import APIKey, Manufacturer
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

    key = create_key()
    return render_template('generate_api_key.html', key=key)

#####################################################################

#################
#  User Routes  #
#################

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
    Gets the first x manufacturesr where x = limi,
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


def get_first_10_manufs():
    '''
    Gets the first 10 manufacturers,
    and returns a list of serialized dicts with the manufacturers' info
    '''
    manufs = Manufacturer.query.limit(10).all()
    if manufs:
        serialized = [m.serialize() for m in manufs]
        return ({'manufacturers': serialized}, 200)
    return ({'manufacturers': []}, 200)


@app.route('/api/get-manufacturers', methods=['GET'])
def get_manufacturers():
    '''Get manufacturers'''
    data = request.json
    name = data.get('name')
    limit = data.get('limit')

    if name:
        result = get_manuf_by_name(name)
    if limit:
        result = get_manuf_by_limit(limit)
    if not result:
        result = get_first_10_manufs()

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


# Manufacturer Routes
#####################################################################

@app.route('/api/add-manufacturers', methods=['POST'])
def add_manufacturers():
    pass


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
    pass


@app.route('/api/update-phones', methods=['PATCH'])
def update_phones():
    pass


@app.route('/api/delete-phones', methods=['DELETE'])
def delete_phones():
    pass

#####################################################################
