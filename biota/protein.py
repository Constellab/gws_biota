from biota.entity import Entity

####################################################################################
#
# Protein class
#
####################################################################################

class Protein(Entity):
    _table_name = 'protein'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta():
        table_name = 'protein'


