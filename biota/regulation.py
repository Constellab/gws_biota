from biota.organism import Organism


####################################################################################
#
# Regulation class
#
####################################################################################

class Regulation(Organism):
    _table_name = 'regulation'

    class Meta():
        table_name = 'regulation'
