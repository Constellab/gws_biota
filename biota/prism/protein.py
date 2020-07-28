# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from biota.prism.entity import Entity

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


