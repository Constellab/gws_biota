# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField

from gws.controller import Controller
from gws.model import Resource

from biota.base import Base
from biota.taxonomy import Taxonomy

class Organism(Base):
    """
    This class represents living organisms
    """

    name = CharField(null=True, index=True)
    taxonomy = ForeignKeyField(Taxonomy, backref = 'organisms', null = True)
    _table_name = 'biota_organism'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
