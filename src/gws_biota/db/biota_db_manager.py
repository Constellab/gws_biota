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

    HOST = "gws_biota-db-prod-db"
    PORT = 3306
    USER = "gws_biota"
    PASSWORD = "gencovery"
    DB_NAME = "gws_biota"

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
            host=self.HOST,
            port=self.PORT,
            user=self.USER,
            password=self.PASSWORD,
            db_name=self.DB_NAME,
            engine="mariadb",
        )

    def get_name(self) -> str:
        return "db"

    def get_brick_name(self) -> str:
        return "gws_biota"

    def is_lazy_init(self) -> bool:
        """
        If True, the db will be initialized after the app start, and app won't fail if db is not available
        If False, the db will be initialized immediately (not recommended), and app fails if db is not available
        """

        return True

    def auto_init(self) -> bool:
        """
        Disable auto_init because this DB need to be started and downloaded manually
        """

        return False
