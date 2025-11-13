

from gws_core.model.typing_register_decorator import typing_registrator
from peewee import CharField, ForeignKeyField

from ..base.protected_base_model import ProtectedBaseModel
from ..db.biota_db_manager import BiotaDbManager
from ..ontology.ontology import Ontology


@typing_registrator(unique_name="BTO", object_type="MODEL", hide=True)
class BTO(Ontology):
    """
    This class represents BTO terms.

    The BTO (BRENDA Tissue Ontology) is a comprehensive structured
    encyclopedia. It provides terms, classifications, and definitions of tissues, organs, anatomical structures,
    plant parts, cell cultures, cell types, and cell lines of organisms from all taxonomic groups
    (animals, plants, fungis, protozoon) as enzyme sources (https://www.brenda-enzymes.org/).
    BRENDA data are available under the Creative Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

    :property bto_id: id of the bto term
    :type bto_id: class:`peewee.CharField`
    :property name: name of the bto term
    :type name: class:`peewee.CharField`
    """
    bto_id = CharField(null=True, index=True)

    _ancestors = None

    # -- A --
    @property
    def ancestors(self):
        if not self._ancestors is None:
            return self._ancestors
        self._ancestors = []
        query = BTOAncestor.select().where(BTOAncestor.bto == self.id)
        for elt in query:
            self._ancestors.append(elt.ancestor)
        return self._ancestors

    # -- C --
    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `bto` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        BTOAncestor.create_table()

    # -- D --
    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        BTOAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- S --
    def set_bto_id(self, bto_id):
        """
        Set the bto_id accessor

        :param: bto_id: The bto_id accessor
        :type bto_id: str
        """
        self.bto_id = bto_id

    class Meta:
        table_name = 'biota_bto'
        is_table = True

class BTOAncestor(ProtectedBaseModel):
    """
    This class defines the many-to-many relationship between the bto terms and their ancestors

    :property bto: id of the concerned bto term
    :type bto: CharField
    :property ancestor: ancestor of the concerned bto term
    :type ancestor: CharField
    """
    bto = ForeignKeyField(BTO)
    ancestor = ForeignKeyField(BTO)

    class Meta:
        table_name = 'biota_bto_ancestors'
        is_table = True
        indexes = (
            (('bto', 'ancestor'), True),
        )
