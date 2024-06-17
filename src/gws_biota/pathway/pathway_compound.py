

from peewee import CharField

from gws_core.model.typing_register_decorator import typing_registrator
from ..base.base import Base

@typing_registrator(unique_name="PathwayCompound", object_type="MODEL", hide=True)
class PathwayCompound(Base):
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
