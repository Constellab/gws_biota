


from ..base.base_ft import BaseFT


class Ontology(BaseFT):
    """
    This class represents base ontology class.
    """

    _table_name = 'biota_ontology'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
