# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField
from ..base.base import Base

class PathwayCompounds(Base):
    reactome_pathway_id = CharField(null=True, index=True)
    chebi_id = CharField(null=True, index=True)
    species = CharField(null=True, index=True)
    _table_name = 'biota_pathway_compounds'

    @property
    def compound(self):
        from ..compound.compound import Compound
        try:
            c = Compound.get(Compound.chebi_id == self.chebi_id)
            c.species = self.species
            return c
        except:
            return None
    
    @property
    def pathway(self):
        from ..pathway.pathway import Pathway
        try:
            pw = Pathway.get(Pathway.reactome_pathway_id == self.reactome_pathway_id)
            pw.species = self.species
            return pw
        except:
            return None
