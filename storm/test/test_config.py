import os

import pytest

from storm.config import ConfigurationProvider, FromStringTypeCoercionMixin
from storm.config import ImproperlyConfigured, DictConfig, settings


def test_config_abc():
    conf = ConfigurationProvider()

    with pytest.raises(NotImplementedError):
        conf.getstring('key')

    with pytest.raises(NotImplementedError):
        conf.getint('key')

    with pytest.raises(NotImplementedError):
        conf.getfloat('key')

    with pytest.raises(NotImplementedError):
        conf.getbool('key')

    with pytest.raises(NotImplementedError):
        conf.getstring('key', default=None)

    with pytest.raises(NotImplementedError):
        conf.getint('key', default=None)

    with pytest.raises(NotImplementedError):
        conf.getfloat('key', default=None)

    with pytest.raises(NotImplementedError):
        conf.getbool('key', default=None)


def test_from_string():
    class Conf(FromStringTypeCoercionMixin):
        def __init__(self, value):
            self.value = value

        def _get(self, key, default):
            return self.value

    assert Conf('string').getstring('key') == 'string'

    assert Conf('1').getint('key') == 1
    with pytest.raises(ImproperlyConfigured):
        assert Conf('1.1').getint('key') == 1
    with pytest.raises(ImproperlyConfigured):
        Conf('t').getint('key')

    assert Conf('1').getfloat('key') == 1
    assert Conf('1.').getfloat('key') == 1
    assert Conf('1.0').getfloat('key') == 1
    assert Conf('99.9345').getfloat('key') == 99.9345
    assert Conf('-1.2').getfloat('key') == -1.2

    assert Conf('1').getbool('key') == True
    assert Conf('y').getbool('key') == True
    assert Conf('yes').getbool('key') == True
    assert Conf('True').getbool('key') == True
    assert Conf('0').getbool('key') == False
    assert Conf('n').getbool('key') == False
    assert Conf('no').getbool('key') == False
    assert Conf('false').getbool('key') == False
    with pytest.raises(ImproperlyConfigured):
        Conf('bof').getbool('key')


def test_dict_config():
    conf = DictConfig('TEST_', {
        'TEST_KEY': 1,
    })

    assert conf.getint('KEY') == 1
    assert conf.getint('NOKEY', 1) == 1
    with pytest.raises(ImproperlyConfigured):
        assert conf.getint('NOKEY') == 1


def test_env_config():
    assert settings.__class__ == DictConfig
    assert settings._conf_dict == os.environ
