from api.models import Manufacturer, Device


class Validator:
    '''
    Validates JSON and converts it to data useable by the API
    '''

    def __init__(self):
        self.JSON_FUNCTIONS = {
            'manufacturer': self.check_manuf_name,
            'name': self.check_device_name,
            'limit': self.convert_limit,
            'offset': self.convert_offset,
            'is_released': self.convert_is_released
        }

    @classmethod
    def check_convertable(cls, num: str = None):
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

    @classmethod
    def convert_num(cls, minimum: int = None, maximum: int = None, default: int = None, num: str = None) -> int or None:
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
        if cls.check_convertable(num):
            converted_num = int(num)
            if minimum != None and converted_num < minimum:
                return minimum
            if maximum != None and converted_num > maximum:
                return maximum
            return converted_num
        else:
            return default

    @classmethod
    def convert_limit(cls, limit: str = None) -> int:
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
        return cls.convert_num(minimum=1, maximum=100, default=100, num=limit)

    @classmethod
    def convert_offset(cls, offset: str = None) -> int:
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
        return cls.convert_num(minimum=0, default=0, num=offset)

    @classmethod
    def convert_id(cls, id: str = None) -> int or None:
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
        return cls.convert_num(default=None, num=id)

    @classmethod
    def convert_is_released(cls, is_released: str = None) -> bool:
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

    @classmethod
    def check_name(cls, name: str = None, model=None):
        ''' Checks if a name can matches the name
        of any rows in the given model table in the DB

        Args:
            name: any string
            model: a model representing a table in the DB
        Returns:
            A boolean representing whether or not the name matches any names in the given
            model's table.
        '''
        if not name or type(name) != str or not model:
            return False
        row_exists = model.query.filter(model.name.ilike(fr'%{name}%')).all()
        if row_exists:
            return True
        return False

    @classmethod
    def check_device_name(cls, name: str = None) -> bool:
        ''' Checks if a device name can matches the name
        of any devices in the DB

        Args:
            name: string that represents a device name
        Returns:
            True if any devices in the DB are similar to name
        '''
        return cls.check_name(name, Device)

    @classmethod
    def check_manuf_name(cls, name: str = None):
        ''' Checks if a manufacturer name can matches the name
        of any devices in the DB

        Args:
            name: string that represents a manufacturer name
        Returns:
            True if any devices in the DB are similar to name
        '''
        return cls.check_name(name, Manufacturer)

    def sanitize_json(self, data: dict = {}, valid_params: list = []) -> dict:
        ''' Validates JSON data and sets any invalid values to defaults

        Args:
            data: a dictionary that holds the passed JSON data
            valid_params: a list of params that are valid for the JSON data
        Returns:
            A dictionary with the values of the valid params in data set to valid data
            for the API
        '''
        if not data or type(valid_params) != list:
            return {}

        if len(list(data.keys())) == 0 or len(valid_params) == 0:
            return {}

        json_data = {}

        for param in valid_params:
            initial_value = data.get(param)
            new_value = self.JSON_FUNCTIONS[param](initial_value)
            if initial_value:
                new_value = self.JSON_FUNCTIONS[param](initial_value)
                # super janky way to check for the val 0 and not include False vals
                if new_value or str(new_value) == '0':
                    if param == 'limit' or param == 'is_released' or param == 'offset':
                        json_data[param] = new_value
                    else:
                        json_data[param] = initial_value
                else:
                    json_data[param] = None
            else:
                if param == 'limit':
                    json_data[param] = 100
                elif param == 'offset':
                    json_data[param] = 0
                else:
                    json_data[param] = None

        return json_data
