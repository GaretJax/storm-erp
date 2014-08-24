"""
Support for working with different sources of configuration values.
"""

import os
from . import types, schema, providers


class DefaultSettings(schema.Settings):
    DEBUG = schema.Value(types.boolean)
    DB_URL = schema.Value(types.sqlalchemy_url)


settings = DefaultSettings(providers.DictConfig(os.environ, prefix='STORM_'))
