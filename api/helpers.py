from datetime import datetime
from sqlalchemy import func

# types of acceptable params for helper funcs that check validity of params
PARAM_TYPES = [int, str]


def check_manuf_name(name: str = None):
    '''
    Checks if the given name matches the name
    of any manufacturers in the DB
    '''
    from api.models import Manufacturer
    if not type(name) == str:
        return False
    manufs = Manufacturer.query.filter(
        func.lower(Manufacturer.name) == func.lower(name)).all()
    if manufs:
        return True
    return False


def check_limit(limit: str = None):
    '''
    Takes a string value for limit,
    checks if it can be converted to an integer,
    and returns True/False based on that
    '''
    if not type(limit) in PARAM_TYPES:
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
    if not type(id) in PARAM_TYPES:
        return None
    try:
        id = int(id)
    except ValueError:
        id = None
    return id


def get_formatted_date(date_str, date_format):
    try:
        return datetime.strptime(date_str, date_format)
    except ValueError:
        return False


def convert_to_date(date_str: str = None):
    '''
    Converts phonearena release date strings into
    datetime dates
    '''
    # If the date is null, we will push it to the back of results by setting to January 1900
    if not date_str:
        return datetime.strptime('January 1900', '%B %Y').date()

    raw_date = None
    # Jan 21, 200 | January 21, 2000 | January, 2000 | January 2000 | 2000
    date_formats = ['%b %d, %Y', '%B %d, %Y', '%B, %Y', '%B %Y', '%Y']
    date_index = 0

    is_converted = False
    while not is_converted:
        if date_index == len(date_formats):
            is_converted = True
            return datetime.strptime('January 1900', '%B %Y').date()
        raw_date = get_formatted_date(date_str, date_formats[date_index])
        if raw_date:
            is_converted = True
        else:
            date_index += 1

    date = raw_date.date()
    return date


def make_date_valid(date_str: str = None):
    '''
    Turns invalid phonearena dates into dates that can be converted
    into datetime dates
    '''
    if not date_str or type(date_str) != str:
        return None

    if '(Official)' in date_str:
        date_str = date_str.replace('(Official)', '')
        date_str = date_str.strip()

    if 'Q1' in date_str:
        date_str = date_str.replace('Q1', 'January')
    if 'Q2' in date_str:
        date_str = date_str.replace('Q2', 'April')
    if 'Q3' in date_str:
        date_str = date_str.replace('Q3', 'July')
    if 'Q4' in date_str:
        date_str = date_str.replace('Q4', 'October')

    # Used for announced devices but not released
    if 'Yes' in date_str:
        # Low effort from phonearena, lower effort from me
        date_str = 'January 1900'

    return date_str
