# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com
#
# ChEBI Copyright Notice and License:
# ChEBI data are available under the Creative Commons License (CC BY 4.0).
# The Creative Commons Attribution License CC BY 4.0 
# is applied to all copyrightable parts of BRENDA. 
# The copyrightable parts of BRENDA are copyright-protected by Prof. Dr. D. Schomburg, Technische 
# Universität Braunschweig, BRICS,Department of Bioinformatics and Biochemistry, 
# Rebenring 56, 38106 Braunschweig, Germany.
# https://www.brenda-enzymes.org
#
# Attribution 4.0 International (CC BY 4.0) information, 2020:
# You are free to:
# * Share — copy and redistribute the material in any medium or format
# * Adapt — remix, transform, and build upon the material
#     for any purpose, even commercially.
# This license is acceptable for Free Cultural Works.
# The licensor cannot revoke these freedoms as long as you follow the license terms.
# https://creativecommons.org/licenses/by/4.0/.

from peewee import CharField, FloatField, IntegerField, ForeignKeyField
from peewee import Model as PeeweeModel

from gws_core import BadRequestException
from ..base.base import Base
from ..db.db_manager import DbManager

class Compound(Base):
    """
    This class represents ChEBI Ontology terms.

    Chemical Entities of Biological Interest (ChEBI) includes an ontological classification, whereby the 
    relationships between molecular entities or classes of entities and their parents and/or children are 
    specified (https://www.ebi.ac.uk/chebi/). ChEBI data are available under the Creative Commons License (CC BY 4.0),
    https://creativecommons.org/licenses/by/4.0/


    :property chebi_id: id of the ChEBI term
    :type chebi_id: class:`peewee.CharField`
    """

    chebi_id = CharField(null=True, index=True)
    kegg_id = CharField(null=True, index=True)
    metacyc_id = CharField(null=True, index=True)
    formula = CharField(null=True, index=True)
    charge = FloatField(null=True, index=True)
    mass = FloatField(null=True, index=True)
    monoisotopic_mass = FloatField(null=True, index=True)
    inchi = CharField(null=True, index=True)
    inchikey = CharField(null=True, index=True)
    smiles = CharField(null=True, index=True)
    chebi_star = CharField(null=True, index=True)

    _ancestors = None
    _table_name = 'biota_compound'
    
    # -- A --

    @property
    def ancestors(self):
        if not self._ancestors is None:
            return self._ancestors

        self._ancestors = []
        Q = CompoundAncestor.select().where(CompoundAncestor.compound == self.id)
        for q in Q:
            self._ancestors.append(q.ancestor)
        
        return self._ancestors

    # -- C --

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `Compound` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        CompoundAncestor.create_table()
        
    
    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `Compound` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        CompoundAncestor.drop_table()
        super().drop_table(*arg, **kwargs)
        
    # -- G --

    
    
    # -- P --
    
    @property
    def pathways(self):
        from .pathway import PathwayCompounds
        try:
            pcomps = PathwayCompounds.select().where(PathwayCompounds.chebi_id == self.chebi_id)
            pathways = []
            for pc in pcomps:
                pw = pc.pathway
                if pw:
                    pathways.append(pc.pathway)
            
            return pathways
        except:
            return None
    
    # -- R --
    
    @property
    def reactions(self):
        from .reaction import ReactionSubstrate, ReactionProduct
        rxns = []
        Q = ReactionSubstrate.select().where(ReactionSubstrate.compound == self)
        for r in Q:
            rxns.append(r.reaction)
            
        Q = ReactionProduct.select().where(ReactionProduct.compound == self)
        for r in Q:
            rxns.append(r.reaction)
            
        return rxns
    
class CompoundAncestor(PeeweeModel):
    """
    This class defines the many-to-many relationship between the compound terms and theirs ancestors

    :type compound: CharField 
    :property compound: id of the concerned compound term
    :type ancestor: CharField 
    :property ancestor: ancestor of the concerned compound term
    """
    
    compound = ForeignKeyField(Compound)
    ancestor = ForeignKeyField(Compound)
    
    class Meta:
        table_name = 'biota_compound_ancestors'
        database = DbManager.db
        indexes = (
            (('compound', 'ancestor'), True),
        )