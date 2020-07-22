from gws.prism.model import Resource

####################################################################################
#
# Ontology class
#
####################################################################################

class Ontology(Resource):
    _table_name = 'ontology'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta():
        table_name = 'ontology'