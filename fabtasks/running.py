import collections
from fabric.api import task, local, hide, env
import six


@task(name='env', alias='e')
def activate_env(name):
    """
    Run subsequent tasks by activating the environment given as parameter.
    """
    try:
        envs = env._active_docker_envs
    except AttributeError:
        envs = env._active_docker_envs = []
    envs.append(name)


def _get_environ():
    environ = collections.OrderedDict(env.docker_envs['*'])
    for k in getattr(env, '_active_docker_envs', []):
        environ.update(env.docker_envs[k])
    return environ


def _get_kwargs():
    kwargs = collections.OrderedDict(env.docker_kwargs['*'])
    for k in getattr(env, '_active_docker_envs', []):
        kwargs.update(env.docker_kwargs.get(k, {}))
    return kwargs


def _rundocker(flavor, cmd='', entrypoint=None, **kwargs):
    args = ['-e {}={}'.format(env.docker_env_prefix + k, v)
            for k, v in six.iteritems(_get_environ())]
    args += ['--{}={}'.format(k, v) for k, v in six.iteritems(_get_kwargs())]
    args += ['--{}={}'.format(k, v) for k, v in six.iteritems(kwargs)]

    if entrypoint:
        args.append('--entrypoint {}'.format(entrypoint))

    with hide('running'):
        local('docker run -t -i --rm {} {}/{} {}'
              .format(' '.join(args), env.package_name, flavor, cmd))


@task
def shell():
    """
    Run a bash shell ready to start the server in a Docker container
    """
    _rundocker('dev', '-i', '/bin/bash')


@task
def run():
    """
    Run the server inside a Docker container. Prefix with the dev task to
    run in development mode or with the prod task to run in production mode.
    """
    _rundocker('dev', env.docker_run_cmd)


@task
def migrate(cmd='-c /etc/alembic.ini upgrade head'):
    """
    Execute the Alembic migration scripts inside a Docker container.
    """
    _rundocker('dev', cmd, 'alembic')


@task
def test(cmd=''):
    _rundocker('test', cmd)
