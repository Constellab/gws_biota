from gena.element import Element

####################################################################################
#
# Relation class
#
####################################################################################

class Relation(Element):
    _table_name = 'relations'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    class Meta:
        table_name = 'relations'