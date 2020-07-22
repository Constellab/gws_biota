from biota.prism.element import Element
from peewee import CharField

####################################################################################
#
# Entity class
#
####################################################################################

class Entity(Element):
    go_id = CharField(null=True, index=True)
    _table_name = 'entity'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def set_go(self, go):
        self.go_id = go
    
    class Meta:
        table_name = 'entity'

