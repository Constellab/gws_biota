

from gws_core.model.typing_register_decorator import typing_registrator
from peewee import CharField, ForeignKeyField

from ..base.base import Base
from ..taxonomy.taxonomy import Taxonomy


@typing_registrator(unique_name="Organism", object_type="MODEL", hide=True)
class Organism(Base):
    """
    This class represents living organisms
    """

    name = CharField(null=True, index=True)
    taxonomy = ForeignKeyField(Taxonomy, backref = 'organisms', null = True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        table_name = 'biota_organism'
        is_table = True
