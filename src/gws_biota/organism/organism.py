

from peewee import CharField, ForeignKeyField

from gws_core.model.typing_register_decorator import typing_registrator
from ..base.base import Base
from ..taxonomy.taxonomy import Taxonomy

@typing_registrator(unique_name="Organism", object_type="MODEL", hide=True)
class Organism(Base):
    """
    This class represents living organisms
    """

    name = CharField(null=True, index=True)
    taxonomy = ForeignKeyField(Taxonomy, backref = 'organisms', null = True)
    _table_name = 'biota_organism'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
