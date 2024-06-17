

import csv
import os

import click
from gws_core import Logger
from .db.db_service import DbService


# Create db
@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
def createdb(ctx):
    DbService.build_biota_db()

@click.pass_context
def create_unicell_db(ctx):
    from .unicell.unicell_service import UnicellService
    UnicellService.create_unicell_db()
