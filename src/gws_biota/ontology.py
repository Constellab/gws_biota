# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField

from gws_core import ResourceDecorator
from .base import Base

@ResourceDecorator("Ontology", hide=True)
class Ontology(Base):
    """
    This class represents base ontology class.
    """

    _table_name = 'biota_ontology'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)