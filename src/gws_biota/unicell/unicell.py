# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com


from peewee import CharField, TextField, ModelSelect, BigBitField
from playhouse.mysql_ext import Match

from gws_core.model.typing_register_decorator import typing_registrator
from ..base.base import Base

@typing_registrator(unique_name="Unicell", object_type="MODEL", hide=True)
class Unicell(Base):
    """
    The unicell
    """

    ft_names = TextField(null=True, index=False)
    compound_map_path = TextField()
    reaction_map_path = TextField()
    compound_to_reaction_path = TextField()
    compound_to_compound_path = TextField()

    _table_name = 'biota_unicell'

    @classmethod
    def after_table_creation(cls) -> None:
        cls.create_full_text_index(['ft_names'], 'I_F_BIOTA_UNICELL')

    @classmethod
    def search(cls, phrase: str, modifier: str = None) -> ModelSelect:
        return cls.select().where(Match((cls.ft_names), phrase, modifier=modifier))