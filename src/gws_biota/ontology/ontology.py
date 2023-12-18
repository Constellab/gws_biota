# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com


from ..base.base_ft import BaseFT


class Ontology(BaseFT):
    """
    This class represents base ontology class.
    """

    _table_name = 'biota_ontology'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
