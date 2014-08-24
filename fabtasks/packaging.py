from __future__ import print_function

import os
import pipes

from fabric.api import settings, task, local, hide, env
from fabric.contrib.console import confirm


def is_working_tree_clean():
    with settings(hide('everything'), warn_only=True):
        local('git update-index -q --ignore-submodules --refresh')
        unstaged = local('git diff-files --quiet --ignore-submodules --',
                         capture=True)
        uncommitted = local('git diff-index --cached --quiet HEAD '
                            '--ignore-submodules --', capture=True)
    return unstaged.succeeded and uncommitted.succeeded


@task
def lint():
    """
    Checks the source code using flake8.
    """
    local('flake8 --statistics --exit-zero --max-complexity=10 '
          '--exclude=\'build,dist,docs,dev\' .')


@task
def authors():
    """
    Updates the AUTHORS file with a list of committers from GIT.
    """
    local('git shortlog -s -e -n | cut -f 2- > AUTHORS')


@task
def release():
    """
    Create a new release and upload it to PyPI.
    """

    if not is_working_tree_clean():
        print('Your working tree is not clean. Refusing to create a release.')
        return

    print('Rebuilding the AUTHORS file to check for modifications...')
    authors()

    if not is_working_tree_clean():
        print(
            'Your working tree is not clean after the AUTHORS file was '
            'rebuilt.'
        )
        print('Please commit the changes before continuing.')
        return

    # Get version
    version = 'v{}'.format(local('python setup.py --version', capture=True))
    name = local('python setup.py --name', capture=True)

    # Tag
    tag_message = '{} release version {}.'.format(name, version)

    print('----------------------')
    print('Proceeding will tag the release, push the repository upstream,')
    print('and release a new version on PyPI.')
    print()
    print('Version: {}'.format(version))
    print('Tag message: {}'.format(tag_message))
    print()
    if not confirm('Continue?', default=True):
        print('Aborting.')
        return

    local('git tag -a {} -m {}'.format(pipes.quote(version),
                                       pipes.quote(tag_message)))

    # Push
    local('git push --tags origin master')

    # Package and upload to pypi
    local('python setup.py sdist bdist_wheel upload')


@task
def package():
    """
    Build a Docker container with the application.

    If skipbuild is specified, the Python package is not rebuilt before
    creating the container.
    """
    from wheel import bdist_wheel
    from distutils.core import Distribution

    dist = Distribution(attrs={
        'name': env.project_name,
        'version': env.project_version,
        'packages': env.package_name,
    })

    cmd = bdist_wheel.bdist_wheel(dist)
    cmd.universal = True
    # TODO: This builds the development setup right now!
    # filename = cmd.get_archive_basename() + '.whl'

    local('time docker run -u {}:{} -w /src -v {}:/src python-dev '
          'python3 setup.py bdist_wheel --universal'.format(
              os.getuid(), os.getgid(), os.path.realpath('.')))


@task
def build(flavor):
    local('time docker-build -t {}/{flavor} -f docker/{flavor} .'
          .format(env.package_name, flavor=flavor))
