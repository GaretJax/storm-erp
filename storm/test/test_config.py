import os
import pytest

from sqlalchemy.engine import url

from storm.config.providers import ConfigurationProvider, DictConfig
from storm.config.providers import NOT_PROVIDED
from storm.config.schema import BoundValue, Settings, Value, ref
from storm.config.schema import ImproperlyConfigured
from storm.config import settings, types


def test_config_abc():
    conf = ConfigurationProvider()

    with pytest.raises(NotImplementedError):
        conf.get('key')


def test_dict_config():
    conf = DictConfig({
        'TEST_KEY': 1,
    }, prefix='TEST_')

    assert conf.get('KEY') == 1
    assert conf.get('NOKEY') is NOT_PROVIDED


def test_simple():
    class SimpleSettings(Settings):
        INTKEY = Value(int)
        STRKEY = Value(str)
        NOKEY = Value(str)
        DEFKEY = Value(str, default='hello')

    assert isinstance(SimpleSettings.INTKEY, BoundValue)

    s = SimpleSettings(DictConfig({
        'INTKEY': '1',
        'STRKEY': 'string'
    }))
    assert s.INTKEY == 1
    assert s.STRKEY == 'string'
    assert s.DEFKEY == 'hello'

    with pytest.raises(ImproperlyConfigured):
        s.NOKEY


def test_readonly():
    class SimpleSettings(Settings):
        KEY = Value(int)

    s = SimpleSettings(DictConfig({
        'KEY': '1',
    }))
    assert s.KEY == 1

    with pytest.raises(AttributeError):
        s.KEY = 2

    assert s.KEY == 1


def test_reference():
    class RefSettings(Settings):
        KEY1 = Value(int)
        KEY2 = Value(int, default=ref('KEY1'))

    s = RefSettings(DictConfig({
        'KEY1': '1',
        'KEY2': '2',
    }))

    assert s.KEY1 == 1
    assert s.KEY2 == 2

    s = RefSettings(DictConfig({
        'KEY1': '1',
    }))

    assert s.KEY1 == 1
    assert s.KEY2 == 1


def test_mixin():
    class TestMixin:
        KEY = Value(int)

    class SimpleSettings(TestMixin, Settings):
        pass

    class SimpleSettingsOverride(TestMixin, Settings):
        KEY = Value(str)

    assert isinstance(SimpleSettings.KEY, BoundValue)
    assert isinstance(SimpleSettingsOverride.KEY, BoundValue)

    s = SimpleSettings(DictConfig({
        'KEY': '1'
    }))
    assert s.KEY == 1

    s = SimpleSettingsOverride(DictConfig({
        'KEY': 'string'
    }))
    assert s.KEY == 'string'


def test_iter():
    class SimpleSettings(Settings):
        KEY1 = Value(int)
        KEY2 = Value(int)
        KEY3 = Value(int)
        KEY4 = Value(int)
        KEY5 = Value(int)

    s = SimpleSettings(DictConfig({
        'KEY1': '10',
        'KEY2': '20',
        'KEY3': '30',
        'KEY4': '40',
        'KEY5': '50',
    }))

    assert list(s.keys()) == [
        'KEY1',
        'KEY2',
        'KEY3',
        'KEY4',
        'KEY5',
    ]
    assert list(s.items()) == [
        ('KEY1', 10),
        ('KEY2', 20),
        ('KEY3', 30),
        ('KEY4', 40),
        ('KEY5', 50),
    ]
    assert s.as_dict() == {
        'KEY1': 10,
        'KEY2': 20,
        'KEY3': 30,
        'KEY4': 40,
        'KEY5': 50,
    }


def test_boolean():
    assert types.boolean('y')
    assert types.boolean('yes')
    assert types.boolean('1')
    assert types.boolean('true')
    assert types.boolean('on')
    assert not types.boolean('n')
    assert not types.boolean('')
    assert not types.boolean('no')
    assert not types.boolean('false')
    assert not types.boolean('off')
    assert not types.boolean('0')


def test_sqlalchemy_url():
    val = types.sqlalchemy_url('postgres://user:password@host/database')
    assert isinstance(val, url.URL)


# def test_validate():
#     class SimpleSettings(Settings):
#         KEY = Value(int)
#
#     s = SimpleSettings(DictConfig({}))
#     with pytest.raises(ImproperlyConfigured):
#         s.validate()
#
#     s = SimpleSettings(DictConfig({
#         'KEY': '1',
#     }))
#     s.validate()
#
#     s = SimpleSettings(DictConfig({
#         'KEY': 'string'
#     }))
#     with pytest.raises(ImproperlyConfigured):
#         s.validate()


def test_env_config():
    assert settings.config_provider.__class__ == DictConfig
    assert settings.config_provider._conf_dict == os.environ
