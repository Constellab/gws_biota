# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import BadRequestException, Logger, Settings
from gws_core.extra import SystemService
from peewee import Model

from ..db.db_manager import DbManager

IS_IPYTHON_ACTIVE = False
try:
    get_ipython
    IS_IPYTHON_ACTIVE = True
except:
    pass


class SimpleBaseModel(Model):

    _is_table_warning_printed = False
    _db_manager = DbManager

    # -- C --

    @classmethod
    def _is_protected(cls):
        # always protect in notebooks
        if IS_IPYTHON_ACTIVE:
            cls._print_warning("The BIOTA db is protected in notebooks")
            return True

        # always protect in prod mode
        if cls._db_manager.mode == "prod":
            cls._print_warning("The prod BIOTA db is protected and cannot be altered")
            return True

        # check protection in dev mode
        if cls._db_manager.mode == "dev":
            if hasattr(cls._db_manager, "_DEACTIVATE_PROTECTION_") and cls._db_manager._DEACTIVATE_PROTECTION_:
                cls._print_warning("The BIOTA protection is DEACTIVATED")
                return False
            else:
                cls._print_warning("The dev BIOTA db is protected and cannot be altered")
                return True

        return False

    @classmethod
    def _print_warning(cls, msg):
        if not cls._is_table_warning_printed:
            Logger.warning(msg)
            cls._is_table_warning_printed = True

    @classmethod
    def create_table(cls, *args, **kwargs):
        if cls._is_protected():
            return
        super().create_table(*args, **kwargs)

    # -- D --

    @classmethod
    def delete(cls, *args, **kwargs):
        if cls._is_protected():
            return False
        return super().delete(*args, **kwargs)

    @classmethod
    def drop_table(cls, *args, **kwargs):
        if cls._is_protected():
            return
        super().drop_table(*args, **kwargs)

    # -- S --

    def save(self, *args, **kwargs):
        if self._is_protected():
            return False
        return super().save(*args, **kwargs)

    class Meta:
        table_name = 'biota_protected_model'
        database = DbManager.db
