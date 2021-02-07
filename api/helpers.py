from datetime import datetime


def check_manuf_name(name: str = None):
    '''
    Checks if the given name matches the name
    of any manufacturers in the DB
    '''
    from api.models import Manufacturer
    manuf = Manufacturer.query.all()
    manufs = [m for m in manuf if m.name.lower() == name.lower()]
    if manufs:
        return True
    return False


def check_limit(limit: str = None):
    '''
    Takes a string value for limit,
    checks if it can be converted to an integer,
    and returns True/False based on that
    '''
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
    try:
        id = int(id)
    except TypeError:
        id = None
    return id


def convert_to_date(date_str: str = None):
    '''
    Converts phonearena release date strings into
    datetime dates
    '''
    raw_date = None
    # If the date is null, we will push it to the back of results by setting to January 1900
    if not date_str:
        return datetime.strptime('January 1900', '%B %Y').date()
    # Phonearena does not have consistent date formatting, so this handles that
    try:
        # Jan 21, 2000
        raw_date = datetime.strptime(date_str, '%b %d, %Y')
    except ValueError:
        try:
            # January, 2000
            raw_date = datetime.strptime(date_str, '%B, %Y')
        except ValueError:
            try:
                # January 2000
                raw_date = datetime.strptime(date_str, '%B %Y')
            except ValueError:
                # 2000
                raw_date = datetime.strptime(date_str, '%Y')

    date = raw_date.date()
    return date


def make_date_valid(date_str: str = None):
    '''
    Turns invalid phonearena dates into dates that can be converted
    into datetime dates
    '''
    if '(Official)' in date_str:
        date_str = date_str.replace('(Official)', '')
        date_str = date_str.strip()

    if 'Q1' in date_str:
        date_str = date_str.replace('Q1', 'January')
    if 'Q2' in date_str:
        date_str = date_str.replace('Q2', 'April')
    if 'Q3' in date_str:
        date_str = date_str.replace('Q2', 'July')
    if 'Q4' in date_str:
        date_str = date_str.replace('Q2', 'October')

    if 'Yes' in date_str:
        # Low effort form phonearena, lower effort from me
        date_str = 'January 1900'

    return date_str
