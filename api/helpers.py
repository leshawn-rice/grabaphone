from datetime import datetime
from sqlalchemy import func
from flask import abort, make_response, jsonify
from api.config import DATE_FORMATS, INVALID_DATE_MAP


def convert_limit(limit):
    if check_limit(limit):
        return int(limit) if int(limit) <= 100 else 100
    else:
        return 100


def convert_is_released(is_released):
    return bool(is_released)


def check_device_name(device):
    if device and type(device) == str:
        return True
    else:
        return False


def handle_json(json_data):
    for key in json_data.keys():
        if not json_data[key]:
            json_response = jsonify({'message': f'Error! {key} invalid!'})
            response = make_response(json_response, 400)
            abort(response)
        if json_data[key] == 'not-sent':
            if key == 'limit':
                json_data[key] = 100
            else:
                json_data[key] = None


def validate_json(data, valid_params):
    json_data = {}

    for param in valid_params:
        param_value = data.get(param)
        param_validator = JSON_PARAM_FUNCS[param](param_value)
        if param_value:
            param_validator = JSON_PARAM_FUNCS[param](param_value)
            if param_validator:
                json_data[param] = param_value if param != 'limit' and param != 'is_released' else param_validator
            else:
                json_data[param] = None
        else:
            json_data[param] = 'not-sent'

    return json_data


def check_manuf_name(name: str = None):
    '''
    Checks if the given name matches the name
    of any manufacturers in the DB
    '''
    from api.models import Manufacturer
    if not type(name) == str:
        return False
    is_manufs = Manufacturer.query.filter(Manufacturer.name.ilike(name)).all()
    if is_manufs:
        return True
    return False


def check_limit(limit: str = None):
    '''
    Takes a string value for limit,
    checks if it can be converted to an integer,
    and returns True/False based on that
    '''
    if type(limit) is not str and type(limit) is not int:
        return False
    try:
        limit = int(limit)
        return True
    except ValueError:
        return False


def convert_manuf_id(id: str = None):
    '''
    Converts id into either an int or None
    and returns it
    '''
    # If invalid type, return None
    if type(id) is not str and type(id) is not int:
        return None
    try:
        id = int(id)
    except ValueError:
        id = None
    return id


def convert_to_date(date_str: str = None):
    '''
    Converts phonearena release date strings into
    datetime dates
    '''
    # If the date is null, we will push it to the back of results by setting to January 1900
    if not date_str or not type(date_str) == str:
        return datetime.strptime('January 1900', '%B %Y').date()

    raw_date = None
    date = None

    for date_format in DATE_FORMATS:
        try:
            raw_date = datetime.strptime(date_str, date_format)
        except ValueError:
            continue

    if raw_date:
        date = raw_date.date()
    else:
        date = datetime.strptime('January 1900', '%B %Y').date()

    return date


def make_date_valid(date_str: str = None):
    '''
    Turns invalid phonearena dates into dates that can be converted
    into datetime dates
    '''
    if not date_str or type(date_str) != str:
        return None

    for invalid_date, valid_date in INVALID_DATE_MAP.items():
        if invalid_date in date_str:
            date_str = date_str.replace(invalid_date, valid_date)

    date_str = date_str.strip()

    return date_str


JSON_PARAM_FUNCS = {
    'manufacturer': check_manuf_name,
    'name': check_device_name,
    'limit': convert_limit,
    'is_released': convert_is_released
}
