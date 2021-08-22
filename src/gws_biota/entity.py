# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField
from .base import Base
from gws_core import ResourceDecorator

@ResourceDecorator("Entity", hide=True)
class Entity(Base):
    """
    This class represents base molecular entities
    
    :property go_id : GO term id
    :type go_id : class:`peewee.CharField`
    """

    go_id = CharField(null=True, index=True)
    _table_name = 'biota_entity'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def set_go(self, go):
        self.go_id = go
    