from biota.element import Element

####################################################################################
#
# Relation class
#
####################################################################################

class Relation(Element):
    _table_name = 'relation'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    class Meta:
        table_name = 'relation'