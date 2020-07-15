import click
from gws.settings import Settings

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
@click.option('--output', '-o', help='Output path')
def createdb(ctx,output):
    print("Hello", output)
    print("Welcome in the CLI!")