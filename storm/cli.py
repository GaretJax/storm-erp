import click


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


from .web.runner import runserver
main.add_command(runserver)

from .database.cli import initdb, migrate
main.add_command(initdb)
main.add_command(migrate)
