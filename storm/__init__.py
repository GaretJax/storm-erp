"""
STORM

MIT License. See LICENSE for more details.
Copyright (c) 2014, Jonathan Stoppani
"""

from os.path import dirname, join


def get_commit():
    try:
        with open(join(dirname(__file__), 'COMMIT')) as fh:
            return fh.read().strip()
    except:
        return 'develop'


__version__ = '0.1.0'
__commit__ = get_commit()
__url__ = 'https://github.com/GaretJax/storm-erp'
