import os
from typing import Union

from gws_core import AbstractDbManager, DbConfig, DbMode, Settings
from peewee import DatabaseProxy


class BiotaDbManager(AbstractDbManager):
    """
    DbManager class.

    Provides backend features for managing databases.
    """

    db = DatabaseProxy()

    _DEACTIVATE_PROTECTION_ = False

    _instance: Union["BiotaDbManager", None] = None

    @classmethod
    def get_instance(cls) -> "BiotaDbManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_config(self, mode: DbMode) -> DbConfig:
        if mode == "test":
            return Settings.get_test_db_config()
        else:
            return self.get_prod_db_config()

    def get_prod_db_config(self) -> DbConfig:
        return DbConfig(
            host=os.environ.get("GWS_BIOTA_DB_HOST"),
            user=os.environ.get("GWS_BIOTA_DB_USER"),
            password=os.environ.get("GWS_BIOTA_DB_PASSWORD"),
            port=int(os.environ.get("GWS_BIOTA_DB_PORT")),
            db_name=os.environ.get("GWS_BIOTA_DB_NAME"),
            engine="mariadb",
        )

    def get_name(self) -> str:
        return "db"

    def get_brick_name(self) -> str:
        return "gws_biota"
