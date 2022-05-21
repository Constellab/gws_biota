# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from typing import List
from gws_core import BadRequestException, Logger, Model, Settings
from peewee import CharField, DoesNotExist, ModelSelect
from playhouse.mysql_ext import Match

from ..db.db_manager import DbManager
from .protected_base_model import ProtectedBaseModel

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


class Base(Model,ProtectedBaseModel):

    name = CharField(null=True, index=True)
    _db_manager = DbManager
    _is_table_warning_printed = False


    @classmethod
    def after_table_creation(cls) -> None:
        cls.create_full_text_index(['name'], 'I_F_BIOTA_BASE')

    @classmethod
    def search(cls, phrase: str, modifier: str = None) -> ModelSelect:
        return cls.select().where(Match((cls.name), phrase, modifier=modifier))

    # -- G --

    @classmethod
    def get_or_none(cls, *arg, **kwargs):
        try:
            return cls.get(*arg, **kwargs)
        except DoesNotExist:
            return None
        except Exception as err:
            raise BadRequestException("An unexpected error occured") from err

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

    class Meta:
        database = DbManager.db
