from gws.prism.model import Resource

####################################################################################
#
# annotation class
#
####################################################################################

class Annotation(Resource):
    _table_name = 'annotation'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    class Meta:
        table_name = 'annotation'