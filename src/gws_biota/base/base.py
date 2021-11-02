# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import BadRequestException, Model, Settings, Logger
from peewee import CharField, ModelSelect

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
    _default_full_text_column = "name"
    _db_manager = DbManager

    __settings = None
    __is_table_warning_printed = False
    # -- C --

    @classmethod
    def create_table(cls, *args, **kwargs):
        if IS_IPYTHON_ACTIVE:
            if not Base.__is_table_warning_printed:
                Logger.warning("Cannot create Biota tables of in ipython notebooks")
                Base.__is_table_warning_printed = True
            return
        if not Base.__settings:
            Base.__settings = Settings.retrieve()
        if Base.__settings.is_test and Base.__settings.is_prod:
            raise BadRequestException("Cannot create Biota tables of the production Biota DB during unit testing")
        super().create_table(*args, **kwargs)

    # -- D --

    def delete(self, *args, **kwargs):
        if IS_IPYTHON_ACTIVE:
            if not Base.__is_table_warning_printed:
                Logger.warning("Cannot delete Biota entries in ipython notebooks")
                Base.__is_table_warning_printed = True
            return False
        
        if not Base.__settings:
            Base.__settings = Settings.retrieve()
        if Base.__settings.is_test and Base.__settings.is_prod:
            raise BadRequestException("Cannot delete Biota entries of the production Biota DB during unit testing")
        return super().delete(*args, **kwargs)

    @classmethod
    def drop_table(cls, *args, **kwargs):
        if IS_IPYTHON_ACTIVE:
            if not Base.__is_table_warning_printed:
                Logger.warning("Cannot drop Biota tables in ipython notebooks")
                Base.__is_table_warning_printed = True
            return
        if not Base.__settings:
            Base.__settings = Settings.retrieve()
        if Base.__settings.is_test and Base.__settings.is_prod:
            raise BadRequestException("Cannot drop Biota tables of the production Biota DB during unit testing")
        super().drop_table(*args, **kwargs)

    # -- G --

    def get_name(self) -> str:
        """
        Get the name. Alias of :meth:`get_title`

        :param: name: The name
        :type name: str
        """

        return self.name

    # -- S --
    
    def save(self, *args, **kwargs):
        if IS_IPYTHON_ACTIVE:
            if not Base.__is_table_warning_printed:
                Logger.warning("Cannot save Biota entries in ipython notebooks")
                Base.__is_table_warning_printed = True
            return False
        if not Base.__settings:
            Base.__settings = Settings.retrieve()
        if Base.__settings.is_test and Base.__settings.is_prod:
            raise BadRequestException("Cannot save Biota entries of the production Biota DB during unit testing")
        return super().save(*args, **kwargs)

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

    @classmethod
    def search(cls, phrase: str, in_boolean_mode: bool = False) -> ModelSelect:
        return super().search(phrase, in_boolean_mode).order_by(cls.name)

    class Meta:
        database = DbManager.db
