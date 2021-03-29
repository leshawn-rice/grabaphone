from datetime import datetime, date
from api.config import DATE_FORMATS, INVALID_DATE_MAP


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


# CHECK IF NECESSARY ANYMORE

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
