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
from .eco.eco import ECOAncestor

from .db.db_service import DbService

# Create db
@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
def createdb(ctx):
    from .db.db_manager import DbManager
    DbManager.init(mode="dev")
    DbManager._DEACTIVATE_PROTECTION_ = True

    if ECO.table_exists():
        BaseModelService.drop_tables()
    
    if ECO.table_exists():
        if ECO.select().count():
            raise BadRequestException("A none empty biota database already exists")

    BaseModelService.drop_tables()
    BaseModelService.create_tables()
    ModelService.register_all_processes_and_resources()
    UserService.create_sysuser()
    
    if not ECO.table_exists():
        raise BadRequestException("Cannot create tables")
    
    if not ECOAncestor.table_exists():
        raise BadRequestException("Cannot create ancestor tables")

    try:
        DbService.build_biota_db()
    except Exception as err:
        Logger.error(err)
