


from ..base.base_ft import BaseFT


class Ontology(BaseFT):
    """
    This class represents base ontology class.
    """


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        table_name = 'biota_ontology'
        is_table = True
