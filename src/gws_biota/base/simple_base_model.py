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

    __settings = None
    __is_table_warning_printed = False

    # -- C --

    @classmethod
    def _check_protection(cls):
        if IS_IPYTHON_ACTIVE:
            if not SimpleBaseModel.__is_table_warning_printed:
                Logger.warning("Cannot alter BIOTA db in ipython notebooks")
                SimpleBaseModel.__is_table_warning_printed = True
            return False
        if not SimpleBaseModel.__settings:
            SimpleBaseModel.__settings = Settings.retrieve()
        if SimpleBaseModel.__settings.is_prod:
            Logger.info("The production BIOTA db is protected and cannot be altered")
            #raise BadRequestException("Cannot alter production production BIOTA db")

        return True

    @classmethod
    def create_table(cls, *args, **kwargs):
        if cls._check_protection():
            super().create_table(*args, **kwargs)

    # -- D --

    @classmethod
    def delete(cls, *args, **kwargs):
        if cls._check_protection():
            return super().delete(*args, **kwargs)
        else:
            return False

    @classmethod
    def drop_table(cls, *args, **kwargs):
        if cls._check_protection():
            super().drop_table(*args, **kwargs)

    # -- S --

    def save(self, *args, **kwargs):
        if self._check_protection():
            return super().save(*args, **kwargs)
        else:
            return False

    class Meta:
        table_name = 'biota_protected_model'
        database = DbManager.db
