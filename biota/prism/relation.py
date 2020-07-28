# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from biota.prism.element import Element

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