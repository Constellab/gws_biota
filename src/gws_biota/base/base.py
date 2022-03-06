# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import Logger, Model, Settings
from peewee import CharField, ModelSelect
from playhouse.mysql_ext import Match

from ..db.db_manager import DbManager

# ####################################################################
#
# Base class
#
# ####################################################################

IS_IPYTHON_ACTIVE = False
try:
    get_ipython
    IS_IPYTHON_ACTIVE = True
except:
    pass


class Base(Model):

    name = CharField(null=True, index=True)
    _db_manager = DbManager

    __settings = None
    __is_table_warning_printed = False

    # -- C --

    @classmethod
    def _check_protection(cls):
        if IS_IPYTHON_ACTIVE:
            if not Base.__is_table_warning_printed:
                Logger.warning("Cannot alter BIOTA db in ipython notebooks")
                Base.__is_table_warning_printed = True
            return False

        if cls._db_manager.mode != "test":
            if not Base.__is_table_warning_printed:
                Logger.warning("The dev and prod BIOTA db are protected and cannot be altered")
                Base.__is_table_warning_printed = True
            return False

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

    @classmethod
    def after_table_creation(cls) -> None:
        cls.create_full_text_index(['name'], 'I_F_BIOTA_BASE')

    @classmethod
    def search(cls, phrase: str, modifier: str = None) -> ModelSelect:
        return cls.select().where(Match((cls.name), phrase, modifier=modifier))
    # -- G --

    def get_name(self) -> str:
        """
        Get the name. Alias of :meth:`get_title`

        :param: name: The name
        :type name: str
        """

        return self.name

    # -- S --

    def set_name(self, name: str):
        """
        Set the name.

        :param: name: The name
        :type name: str
        """

        self.name = name

    @classmethod
    def search_by_name(cls, name, page: int = 1, number_of_items_per_page: int = 50):
        Q = cls.select().where(cls.name ** name).paginate(page, number_of_items_per_page)
        return Q

    def save(self, *args, **kwargs):
        if self._check_protection():
            return super().save(*args, **kwargs)
        else:
            return False

    class Meta:
        database = DbManager.db
