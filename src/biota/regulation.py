from biota.organism import Organism


####################################################################################
#
# Regulation class
#
####################################################################################

path_test = os.path.realpath('./databases_input') #Set the path where we can find input data

class Regulation(Organism):
    _table_name = 'regulation'
    pass

    class Meta():
        table_name = 'regulation'
