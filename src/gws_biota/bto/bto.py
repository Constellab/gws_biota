# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel

from gws_core.model.typing_register_decorator import typing_registrator
from ..ontology.ontology import Ontology
from ..base.base import Base
from ..db.db_manager import DbManager

@typing_registrator(unique_name="BTO", object_type="MODEL", hide=True)
class BTO(Ontology):
    """
    This class represents BTO terms.
    
    The BTO (BRENDA Tissue Ontology) is a comprehensive structured 
    encyclopedia. It providies terms, classifications, and definitions of tissues, organs, anatomical structures, 
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

    _table_name = 'biota_bto'

    # -- A --

    @property
    def ancestors(self):
        if not self._ancestors is None:
            return self._ancestors

        self._ancestors = []
        Q = BTOAncestor.select().where(BTOAncestor.bto == self.id)
        for q in Q:
            self._ancestors.append(q.ancestor)
        
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

    # -- G --

    # -- S --

    def set_bto_id(self, bto_id):
        """
        Set the bto_id accessor

        :param: bto_id: The bto_id accessor
        :type bto_id: str
        """
        self.bto_id = bto_id

class BTOAncestor(PWModel):
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
        database = DbManager.db
        indexes = (
            (('bto', 'ancestor'), True),
        )
