# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField

from gws_core.model.typing_register_decorator import typing_registrator
from ..db.db_manager import DbManager
from ..base.base import Base
from ..base.protected_base_model import ProtectedBaseModel
from ..ontology.ontology import Ontology
from ..taxonomy.taxonomy import Taxonomy
from ..compound.compound import Compound
from .pathway_compound import PathwayCompound

@typing_registrator(unique_name="Pathway", object_type="MODEL", hide=True)
class Pathway(Ontology):
    """
    This class represents reactome Pathways 
    """
    
    reactome_pathway_id = CharField(null=True, index=True)
    _ancestors = None
    
    _table_name = 'biota_pathways'

    # -- A --

    @property
    def ancestors(self):
        if not self._ancestors is None:
            return self._ancestors
        self._ancestors = []
        Q = PathwayAncestor.select().where(PathwayAncestor.pathway == self.id)
        for q in Q:
            self._ancestors.append(q.ancestor)
        return self._ancestors
    
    # -- C --

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `pwo` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        
        if not Compound.table_exists():
            Compound.create_table()
        super().create_table(*args, **kwargs)
        PathwayAncestor.create_table()
        PathwayCompound.create_table()

    # -- D --

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `pwo` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        PathwayAncestor.drop_table()
        PathwayCompound.drop_table()
        super().drop_table(*arg, **kwargs)

class PathwayAncestor(ProtectedBaseModel):
    """
    This class defines the many-to-many relationship between the pathway and theirs ancestors

    :type pathway: CharField 
    :property pathway: id of the concerned pathway
    :type ancestor: CharField 
    :property ancestor: ancestor of the concerned pathway term
    """

    pathway = ForeignKeyField(Pathway)
    ancestor = ForeignKeyField(Pathway)
    
    class Meta:
        table_name = 'biota_pathway_ancestors'
        database = DbManager.db
        indexes = (
            (('pathway', 'ancestor'), True),
        )
