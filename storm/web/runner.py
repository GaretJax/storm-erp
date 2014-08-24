import os

import click


DEFAULT_INTERFACE = '0.0.0.0'
DEFAULT_PORT = 5000


def load_config(debug, prefix):
    def k(s):
        return '{}_{}'.format(prefix, s)

    if debug:
        os.environ[k('DEBUG')] = '1'
        os.environ.setdefault(k('SECRET_KEY'), 'changeme')
    elif k('DEBUG') in os.environ:
        del os.environ[k('DEBUG')]


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


@click.command()
@click.option('--debug/--no-debug', '-d', default=False)
@click.argument('interface', required=False)
def runserver(debug, interface):
    """
    Run a uWSGI backed production-grade web server for the STORM application.
    """

    package = __name__.split('.', 1)[0]

    load_config(debug, package.upper())

    if not interface:
        interface = '{}:{}'.format(DEFAULT_INTERFACE, DEFAULT_PORT)
    else:
        if ':' not in interface:
            interface = '{}:{}'.format(interface, DEFAULT_PORT)
        elif interface.startswith(':'):
            interface = '{}{}'.format(DEFAULT_INTERFACE, interface)

    cmdargs = [
        'uwsgi',
        '--master',
        '--workers', '4',
        '--procname-master', 'prodmgr-master',
        '--procname', 'prodmgr-worker',
        '--auto-procname',
        '--need-app',
        '--enable-threads',
        '--http', interface,
        '--module', '{}.web.uwsgi'.format(package),
        '--callable', 'app',
    ]

    if debug:
        cmdargs.extend([
            '--py-autoreload', '1',
            '--catch-exceptions',
            '--workers', '1',
            '--threads', '4',
            '--single-interpreter',
        ])

        print('=' * 40)
        print(' WARNING: Running in DEBUG mode')
        print('=' * 40)
        print()

    path = which('uwsgi')

    if not path:
        raise RuntimeError('uWSGI executable not found on path.')

    print('Found uwsgi at "{}"'.format(path))
    os.execv(path, cmdargs)
