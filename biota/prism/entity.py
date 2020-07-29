# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from biota.prism.element import Element
from peewee import CharField

class Entity(Element):
    go_id = CharField(null=True, index=True)
    _table_name = 'entity'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def set_go(self, go):
        self.go_id = go
    
    class Meta:
        table_name = 'entity'

