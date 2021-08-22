# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import csv
import click

from .service.db_service import DbService
from gws_core import User, Study, ModelService, UserService, BadRequestException, Logger
from gws_biota import ECO
# Create db

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
def createdb(ctx):
    if ECO.table_exists():
        if ECO.select().count():
            raise BadRequestException("An none empty biota database already exists")

    ModelService.drop_tables()
    ModelService.create_tables()
    ModelService.register_all_processes_and_resources()
    Study.create_default_instance()
    UserService.create_owner_and_sysuser()

    try:
        DbService.build_biota_db()
    except Exception as err:
        Logger.error(err)

