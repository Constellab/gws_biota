# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import csv
import click


# Create db

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
@click.option('--user', '-u', help='User name')
def createdb(ctx, user):
    from biota._cli.createdb import createdb as do_createdb
    do_createdb(user)