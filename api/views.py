from flask import render_template, request
from app.app import app
from app.database import db
from api.models import APIKey
import os


# Routes that can be accessed by anybody with an API key
@app.route('/api/get-manufacturers', methods=['GET'])
def get_manufacturers():
    pass


@app.route('/api/get-phones', methods=['GET'])
def get_phones():
    pass


@app.route('/api/generate-api-key', methods=['GET', 'POST'])
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
            try:
                # Try to add the key to the db,
                # if the key exists show error message to user
                new_key = APIKey(key=key)
                db.session.add(new_key)
                db.session.commit()
            # Get name of error
            except:
                key = 'KEY COULD NOT BE SAVED'
            return render_template('key_created.html', key=key)

    key_created = False
    key = None
    while not key_created:
        # The result from os.urandom(x) when hexed is twice the length as the val passed in
        random_key = os.urandom(6).hex()
        if not APIKey.query.filter_by(key=random_key).first():
            key_created = True
            key = random_key

    return render_template('generate_api_key.html', key=key)


# Routes that can only be accessed by someone with the secret key (consider simply removing)
@app.route('/api/add-manufacturers', methods=['POST'])
def add_manufacturers():
    pass


@app.route('/api/add-phones', methods=['POST'])
def add_phones():
    pass


@app.route('/api/update-manufacturers', methods=['PATCH'])
def update_manufacturers():
    pass


@app.route('/api/update-phones', methods=['PATCH'])
def update_phones():
    pass


@app.route('/api/delete-manufacturers', methods=['DELETE'])
def delete_manufacturers():
    pass


@app.route('/api/delete-phones', methods=['DELETE'])
def delete_phones():
    pass
