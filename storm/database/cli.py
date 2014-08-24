import click
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from storm.config import settings


def drop_create(url, drop, create, ask):
    if not (drop or create):
        return

    db_name, url.database = url.database, 'postgres'

    engine = create_engine(url)
    connection = engine.connect()
    connection.execute('commit')

    if drop:
        if ask:
            click.confirm('The database {} will be dropped. Are you sure?'
                          .format(click.style(db_name, fg='red')), abort=True)
        click.secho('Dropping database...', fg='green')
        connection.execute('drop database if exists "{}"'.format(db_name))
        connection.execute('commit')
    elif create:
        create = not bool(connection.execute(
            text('select count(*) from pg_database where datname=:db'),
            db=db_name
        ).scalar())

    if drop or create:
        click.secho('Creating database...', fg='green')
        connection.execute('create database "{}"'.format(db_name))
        connection.execute('commit')

    connection.close()


@click.command()
@click.option('--yes/--ask', '-y', 'noinput', default=False,
              help='Don\'t ask for confirmation when dropping databases.')
@click.option('--create/--no-create', '-c', default=False,
              help='Create the database if it does not exists.')
@click.option('--drop/--no-drop', '-d', default=False,
              help=('Drop and recreate the database if it already exists '
                    '(implies -c).'))
@click.pass_context
def initdb(ctx, noinput, create, drop):
    """
    Initialize a database to be used with STORM and applies all the schema
    migrations to it.
    """
    drop_create(settings.DB_URL, drop, create, not noinput)
    ctx.invoke(migrate)


@click.command()
def migrate():
    click.secho('Applying database migrations...', fg='green')
    config = Config()
    config.set_main_option('script_location', 'storm:migrations')
    command.upgrade(config, 'head', sql=False, tag=None)
