"""
Namespace-based settings management

Usage:

    from sermin.config import settings, Setting

    # Define a new namespace by assigning a string label
    settings.myapp = 'My app'

    # Define a new setting by assigning a Setting instance
    settings.myapp.mysetting = Setting()

    # Set a setting's value by assigning a value
    settings.myapp.mysetting = 'hello'

    # Read a setting's value by setting a value
    print(settings.myapp.mysetting)
"""


class Registry(object):
    """
    Setting multiton registry
    """
    def __init__(self):
        self._clear()

    def _clear(self):
        # We're setting, so have to access via __dict__
        self.__dict__['_namespaces'] = {}

    def __getattr__(self, name):
        if name not in self._namespaces:
            raise AttributeError('{!r} object has no attribute {!r}'.format(
                self.__class__, name,
            ))
        return self._namespaces[name]

    def __setattr__(self, name, value):
        """
        Create a new namespace
        """
        if not isinstance(name, str):
            raise ValueError('Namespace label must be a string')
        if name.startswith('_'):
            raise ValueError('Namespace cannot start with an underscore')

        if name in self._namespaces:
            raise ValueError('Namespaces cannot be redefined')

        self._namespaces[name] = Namespace(name, label=value)


settings = Registry()


class Namespace(object):
    def __init__(self, name, label):
        self.__dict__.update({
            '_name': name,
            '_label': label,
            '_settings': {},
        })

    def __getattr__(self, name):
        """
        Get a setting
        """
        # Access a setting
        if name not in self._settings:
            raise AttributeError('{!r} object has no attribute {!r}'.format(
                self.__class__, name,
            ))
        return self._settings[name].get()

    def __setattr__(self, name, value):
        """
        Set a setting's value
        """
        # Can't set namespace variables
        if name.startswith('_'):
            raise ValueError('Settings cannot start with an underscore')

        if name in self._settings:
            # Set an existing setting's value
            if isinstance(value, Setting):
                raise ValueError('Settings cannot be redefined')
            self._settings[name].set(value)
        else:
            # Create a new setting
            if not isinstance(value, Setting):
                raise ValueError(
                    'Settings must be defined before they can be assigned',
                )
            self._settings[name] = value


class Setting(object):
    """
    Setting definitions for modules
    """
    def __init__(self, label, type=None, default=None, list=False):
        """
        Arguments:
            label       Label for argument
            type        Optional type of argument (callable used to cast value)
                        Subclasses can override type parsing in cast()
                        Default: str
            default     Default value for this setting
                        Default: None
            list        Boolean to declare if this is a list or not
        """
        # Store arguments
        self.label = label
        self.type = type
        self.default = default
        self.list = list

        # Set initial value
        self.set(default)

    def set(self, value):
        """
        Parse the value and return it as the specified type

        If the value is None, empties the value

        Raise a ValueError if the value is invalid
        """
        if value is None:
            self.value = [] if self.list else None
        else:
            value = self.cast(value)
            if self.list:
                self.value.append(value)
            else:
                self.value = value

    def cast(self, value):
        if self.type is None:
            return value
        return self.type(value)

    def get(self):
        return self.value

    def __repr__(self):
        return '<Setting {}>'.format(self.value)
