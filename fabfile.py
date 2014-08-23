import six
from os.path import join, dirname
from glob import glob
from fabric.api import env


def loadenv(path):
    gl = {'__file__': path}
    with open(path) as fh:
        exec(compile(fh.read(), path, 'exec'), gl)
    for k, v in six.iteritems(gl):
        if not k.startswith('_'):
            setattr(env, k, v)

loadenv(join(dirname(__file__), 'fabenv.py'))

for path in glob(join(dirname(__file__), 'fabtasks', '*.py')):
    with open(path) as fh:
        exec(compile(fh.read(), path, 'exec'))
