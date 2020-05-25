from hello.element import Element

####################################################################################
#
# Entity class
#
####################################################################################

class Entity(Element):
    _table_name = 'entity'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    class Meta:
        table_name = 'entity'

