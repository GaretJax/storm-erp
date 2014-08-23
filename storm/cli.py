import click


@click.group()
@click.option('--debug/--no-debug', '-d', default=False)
@click.pass_context
def main(ctx, debug):
    ctx.obj = {
        'debug': debug,
    }


from .web.runner import runserver
main.add_command(runserver)
