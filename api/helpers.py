from datetime import datetime
from sqlalchemy import func
from flask import abort, make_response, jsonify
from api.config import DATE_FORMATS, INVALID_DATE_MAP


def check_convertable(num: str = None):
    ''' Checks if a given string can be converted to an integer

    Args:
        num: a string representing an integer, or None
    Returns:
        A boolean representing whether num can be converted to an integer
    >>> check_convertable("5")
    True
    >>> check_convertable("Hello World")
    False
    >>> check_convertable("Seven")
    False
    >>> check_convertable("False")
    False
    '''
    if type(num) is not str and type(num) is not int:
        return False
    try:
        num = int(num)
        return True
    except ValueError:
        return False


def convert_num(minimum: int = None, maximum: int = None, default: int = None, num: str = None) -> int or None:
    ''' Converts a string to a valid integer given constraints minimum, maximum, and default

    Args:
        minimum: any integer or None
        maximum: any integer or None
        default: any integer or None
        num: a string that represents an integer where minimum < num < maximum
    Returns:
        num converted to an integer, minimum if num < minimum, maximum if num > maximum
        or default if num cannot be converted

    >>> convert_num(num=50)
    50
    >>> convert_num(num="50")
    50
    >>> convert_num(num=None) is None
    True
    >>> convert_num(minimum=0, num=-1, default=0)
    0
    >>> convert_num(minimum=1, maximum=100, num=107, default=84)
    100
    '''
    if check_convertable(num):
        converted_num = int(num)
        if minimum != None and converted_num < minimum:
            return minimum
        if maximum != None and converted_num > maximum:
            return maximum
        return converted_num
    else:
        return default


def convert_limit(limit: str = None) -> int:
    ''' Converts a limit string to a valid limit

    Args:
        limit: a string that represents an integer where 1 <= limit <= 100
    Returns:
        limit converted to an integer, 1 if limit < 1, 100 if limit > 100 or limit cannot be converted

    >>> convert_limit(50)
    50
    >>> convert_limit("50")
    50
    >>> convert_limit(None)
    100
    >>> convert_limit(-50)
    1
    >>> convert_limit(150)
    100
    '''
    return convert_num(minimum=1, maximum=100, default=100, num=limit)


def convert_offset(offset: str = None) -> int:
    ''' Converts an offset string to a valid offset

    Args:
        offset: a string that represents an integer where limit >= 0
    Returns:
        offset converted to an integer, or 0 if it cannot be converted or is < 0

    >>> convert_offset(50)
    50
    >>> convert_offset("50")
    50
    >>> convert_offset(None)
    0
    >>> convert_offset(-50)
    0
    '''
    return convert_num(minimum=0, default=0, num=offset)


def convert_id(id: str = None) -> int or None:
    ''' Converts an id string to an integer

    Args:
        id: a string that represents an integer
    Returns: 
        id converted to an integer or None if id cannot be converted

    >>> convert_id(50)
    50
    >>> convert_id("50")
    50
    >>> convert_id(None) is None
    True
    >>> convert_id(-50)
    -50
    '''
    return convert_num(default=None, num=id)


def convert_is_released(is_released: str = None) -> bool:
    ''' Converts a str or None to a boolean 

    Args:
        is_released: a string or None
    Returns:
        is_released converted to a boolean

    >>> convert_is_released("I want only released devices")
    True
    >>> convert_is_released()
    False
    >>> convert_is_released(None)
    False
    '''
    return bool(is_released)


def check_name(name: str = None, model=None):
    ''' Checks if a name can matches the name
    of any rows in the given model table in the DB

    Args:
        name: any string
        model: a model representing a table in the DB
    Returns:
        A boolean representing whether or not the name matches any names in the given
        model's table.
    '''
    if not name or type(name) != str:
        return False
    row_exists = model.query.filter(model.name.ilike(fr'%{name}%')).all()
    if row_exists:
        return True
    return False


def check_device_name(name: str = None) -> bool:
    ''' Checks if a device name can matches the name
    of any devices in the DB

    Args:
        name: string that represents a device name
    Returns:
        True if any devices in the DB are similar to name
    '''
    from api.models import Device
    return check_name(name, Device)


def check_manuf_name(name: str = None):
    ''' Checks if a manufacturer name can matches the name
    of any devices in the DB

    Args:
        name: string that represents a manufacturer name
    Returns:
        True if any devices in the DB are similar to name
    '''
    from api.models import Manufacturer
    return check_name(name, Manufacturer)


def handle_json(json_data: dict = None):
    ''' Handles returning an error for invalid data, or setting defaults for data not passed

    Args:
        json_data: a dict of validated json_data i.e. {'key': 123456, 'manufacturer': 'Apple', 'name': 'iPhone' }
    Returns:
        either json_data that has had any necessary defaults set, or aborts with an appropriate response
    '''
    for key in json_data.keys():
        if not json_data[key]:
            json_response = jsonify({'message': f'Error! {key} invalid!'})
            response = make_response(json_response, 400)
            abort(response)
        if json_data[key] == 'not-sent':
            if key == 'limit':
                json_data[key] = 100
            if key == 'offset':
                json_data[key] = 0
            else:
                json_data[key] = None
    return json_data


def validate_json(data: dict = {}, valid_params: list = []):
    ''' Validates JSON data and sets any invalid values to defaults

    Args:
        data: a dictionary that holds the passed JSON data
        valid_params: a list of params that are valid for the JSON data
    Returns:
        A dictionary with the values of the valid params in data set to valid data
        for the API
    '''
    json_data = {}

    for param in valid_params:
        param_value = data.get(param)
        param_validator = JSON_PARAM_FUNCS[param](param_value)
        if param_value:
            param_validator = JSON_PARAM_FUNCS[param](param_value)
            # the str condition is a super janky way to check for the val 0 and not include False vals
            if param_validator or str(param_validator == '0'):
                if param == 'limit' or param == 'is_released' or param == 'offset':
                    json_data[param] = param_validator
                else:
                    json_data[param] = param_value
            else:
                json_data[param] = None
        else:
            json_data[param] = 'not-sent'

    return json_data


def convert_to_date(date_str: str = None):
    ''' Converts phonearena release date strings into
    datetime dates

    Args:
        date_str: a string that represents a date such as May 2015, or Nov 7th, 2020
    Returns:
        A datetime.date object representing the given date, or January 1900 if no date was passed
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
    ''' Turns invalid phonearena dates into dates that can be converted
    into datetime dates

    Args:
        date_str: a string that represents a date such as May 2015
    Returns:
        A valid string that can be converted into a date representing date_str
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
    'offset': convert_offset,
    'is_released': convert_is_released
}
