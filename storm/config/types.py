"""
Common types for settings classes.
"""

from sqlalchemy.engine.url import make_url


def boolean(string):
    return string.lower() in set(['1', 'true', 'yes', 'on', 'y'])


def sqlalchemy_url(string):
    return make_url(string)
