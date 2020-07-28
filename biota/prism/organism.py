# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

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



