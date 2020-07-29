# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from biota.prism.organism import Organism

####################################################################################
#
# Regulation class
#
####################################################################################

class Regulation(Organism):
    _table_name = 'regulation'

    class Meta():
        table_name = 'regulation'
