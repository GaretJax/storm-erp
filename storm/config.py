"""
Support for working with different sources of configuration values.
"""

import os


class ImproperlyConfigured(Exception):
    """
    Raised when e request for a configuration value cannot be fulfilled.
    """


NOT_PROVIDED = object()


class ConfigurationProvider:
    def getstring(self, key, default=NOT_PROVIDED):
        raise NotImplementedError()

    def getint(self, key, default=NOT_PROVIDED):
        raise NotImplementedError()

    def getfloat(self, key, default=NOT_PROVIDED):
        raise NotImplementedError()

    def getbool(self, key, default=NOT_PROVIDED):
        raise NotImplementedError()


class FromStringTypeCoercionMixin:
    def getstring(self, key, default=NOT_PROVIDED):
        return self._get_converted(str, key, default)

    def getint(self, key, default=NOT_PROVIDED):
        return self._get_converted(int, key, default)

    def getfloat(self, key, default=NOT_PROVIDED):
        return self._get_converted(float, key, default)

    def getbool(self, key, default=NOT_PROVIDED):
        def str_to_bool(val):
            if val.lower() in ('1', 'y', 'yes', 'true'):
                return True
            elif val.lower() in ('0', 'n', 'no', 'false'):
                return False
            else:
                raise ValueError()
        return self._get_converted(str_to_bool, key, default)

    def _get_converted(self, type, key, default):
        val = self._get(key, default)
        try:
            return type(val)
        except ValueError:
            raise ImproperlyConfigured(
                'Value of {} cannot be converted to {}'
                .format(key, type.__name__)
            )


class DictConfig(FromStringTypeCoercionMixin, ConfigurationProvider):
    """
    Loads configuration values from the passed dictionary.
    """
    def __init__(self, prefix, conf_dict):
        self._conf_dict = conf_dict
        self._prefix = prefix

    def _get(self, key, default):
        try:
            return self._conf_dict[self._prefix + key]
        except KeyError:
            if default is NOT_PROVIDED:
                raise ImproperlyConfigured('no value set for {}'.format(key))
            else:
                return default


settings = DictConfig('STORM_', os.environ)
