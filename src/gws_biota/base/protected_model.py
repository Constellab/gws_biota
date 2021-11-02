# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import Model
from gws_core import BadRequestException, Settings, Logger
from ..db.db_manager import DbManager

IS_IPYTHON_ACTIVE = False
try:
    get_ipython
    IS_IPYTHON_ACTIVE = True
except:
    pass

class ProtectedModel(Model):
    
    __settings = None
    __is_table_warning_printed = False

    # -- C --

    @classmethod
    def _check_protection(cls):
        if IS_IPYTHON_ACTIVE:
            if not cls.__is_table_warning_printed:
                Logger.warning("Cannot alter Biota tables of in ipython notebooks")
                cls.__is_table_warning_printed = True
            return False

        if not cls.__settings:
            cls.__settings = Settings.retrieve()
        if cls.__settings.is_test and cls.__settings.is_prod:
            raise BadRequestException("Cannot alter Biota tables of the production Biota DB during unit testing")
        
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