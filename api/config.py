import os

MASTER_KEY = os.environ.get('MASTER_KEY', 'masterkey')
# Jan 21, 200 | January 21, 2000 | January, 2000 | January 2000 | 2000
DATE_FORMATS = ['%b %d, %Y', '%B %d, %Y', '%B, %Y', '%B %Y', '%Y']

INVALID_DATE_MAP = {
    '(Official)': '', 'Q1': 'January', 'Q2': 'April', 'Q3': 'July', 'Q4': 'October', 'Yes': 'January 1900'}

UNRELEASED_YEAR = 5
