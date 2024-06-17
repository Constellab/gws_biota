

from peewee import ModelSelect, TextField
from playhouse.mysql_ext import Match

from .base import Base


class BaseFT(Base):

    ft_names = TextField(null=True)

    @classmethod
    def after_table_creation(cls) -> None:
        cls.create_full_text_index(['ft_names'], 'ft_names')

    @classmethod
    def search(cls, phrase: str, modifier: str = None) -> ModelSelect:
        return cls.select().where(Match((cls.ft_names), phrase, modifier=modifier))
