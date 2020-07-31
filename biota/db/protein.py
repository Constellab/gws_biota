# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws.prism.controller import Controller

from biota.db.entity import Entity

class Protein(Entity):
    """
    This class represents proteins.
    """

    _table_name = 'protein'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta():
        table_name = 'protein'


Controller.register_model_classes([Protein])