# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import AbstractDbManager, DbConfig, DbMode, Settings
from peewee import DatabaseProxy

# ####################################################################
#
# DbManager class
#
# ####################################################################


class DbManager(AbstractDbManager):
    """
    DbManager class.

    Provides backend features for managing databases.
    """

    db = DatabaseProxy()

    @classmethod
    def get_config(cls, mode: DbMode) -> DbConfig:
        settings = Settings.retrieve()

        if mode == 'test':
            return settings.get_gws_core_test_db_config()
        else :
            return cls.get_prod_db_config()

    @classmethod
    def get_prod_db_config(cls) -> DbConfig:
        return {
            "host":  "gws_biota_db",
            "user": "gws_biota",
            "password": "gencovery",
            "port": 3306,
            "db_name": "gws_biota",
            "engine": "mariadb"
        }


    @classmethod
    def get_unique_name(cls) -> str:
        return 'gws_biota'


# Activate the biota db if we are in a notebook
try:
    get_ipython
    DbManager.init(mode='dev')
except:
    pass
