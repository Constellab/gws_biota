


from typing import Any

from gws_core import BadRequestException, JSONField, Model
from peewee import CharField, DoesNotExist, ModelSelect
from playhouse.mysql_ext import Match

from ..db.biota_db_manager import BiotaDbManager
from .protected_base_model import ProtectedBaseModel


class Base(Model, ProtectedBaseModel):

    name = CharField(null=True, index=True)
    data: dict[str, Any] = JSONField(default=dict)

    @classmethod
    def after_table_creation(cls) -> None:
        cls.create_full_text_index(['name'], 'name')

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
        db_manager = BiotaDbManager.get_instance()
        is_table = False
        database = db_manager.db
