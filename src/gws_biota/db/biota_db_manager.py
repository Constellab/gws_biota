

import os

from gws_core import AbstractDbManager, DbConfig, DbMode, Settings
from peewee import DatabaseProxy


class BiotaDbManager(AbstractDbManager):
    """
    DbManager class.

    Provides backend features for managing databases.
    """

    db = DatabaseProxy()

    _DEACTIVATE_PROTECTION_ = False

    @classmethod
    def get_config(cls, mode: DbMode) -> DbConfig:

        if mode == 'test':
            settings = Settings.get_instance()
            return settings.get_test_db_config()
        else:
            return cls.get_prod_db_config()

    @classmethod
    def get_prod_db_config(cls) -> DbConfig:
        return {
            "host":  os.environ.get("GWS_BIOTA_DB_HOST"),
            "user": os.environ.get("GWS_BIOTA_DB_USER"),
            "password": os.environ.get("GWS_BIOTA_DB_PASSWORD"),
            "port": int(os.environ.get("GWS_BIOTA_DB_PORT")),
            "db_name": os.environ.get("GWS_BIOTA_DB_NAME"),
            "engine": "mariadb"
        }

    @classmethod
    def get_name(cls) -> str:
        return 'db'

    @classmethod
    def get_brick_name(cls) -> str:
        return 'gws_biota'


# Activate the biota db if we are in a notebook
try:
    get_ipython
    BiotaDbManager.init(mode='dev')
except:
    pass
