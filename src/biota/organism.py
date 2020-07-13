from gws.prism.model import Resource


####################################################################################
#
# Organism class
#
####################################################################################


class Organism(Resource):
    _table_name = 'organism'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta():
        table_name = 'organism'



