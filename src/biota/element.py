from gws.prism.model import Resource

####################################################################################
#
# Element class
#
####################################################################################

class Element(Resource):
    _table_name = 'element'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    class Meta:
        table_name = 'element'