# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import csv
import os

import click
from gws_core import (BadRequestException, Logger, ModelService, User,
                      UserService)
from gws_core.extra import BaseModelService

from gws_biota import ECO

from .db.db_service import DbService

# Create db


@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
def createdb(ctx):
    if ECO.table_exists():
        if ECO.select().count():
            raise BadRequestException("A none empty biota database already exists")

    BaseModelService.drop_tables()
    BaseModelService.create_tables()
    ModelService.register_all_processes_and_resources()
    UserService.create_sysuser()

    try:
        DbService.build_biota_db()
    except Exception as err:
        Logger.error(err)
