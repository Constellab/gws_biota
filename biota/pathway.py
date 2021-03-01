# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField
from peewee import Model as PWModel

from gws.controller import Controller
from gws.model import Resource

from biota.base import Base, DbManager
from biota.ontology import Ontology

class Pathway(Ontology):
    """
    This class represents reactome Pathways 
    """

    reactome_id = CharField(null=True, index=True)
    _ancestors = None
    
    _fts_fields = { **Ontology._fts_fields, 'title': 1.0 }
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
    def create_pathway_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `pwo` database
        
        :param biodata_dir: path of the :file:`pwo.obo`
        :type biodata_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """

        from biota._helper.reactome import Reactome
        
        # insert patwhays
        pathway_dict = Reactome.parse_pathways_to_dict(biodata_dir, kwargs['reactome_pathways_file'])
        pathways = []
        for _pw in pathway_dict:
            pw = Pathway(
                reactome_id = _pw["reactome_pathway_id"],
                data = {
                    "title": _pw["title"],
                    "species": _pw["species"]
                }
            )
            pathways.append(pw)
        
        Pathway.save_all(pathways)

        # insert pathways ancestors
        pathway_rels = Reactome.parse_pathway_relations_to_dict(biodata_dir, kwargs['reactome_pathway_relations_file'])      
        k = 0
        bulk_size = 100
        with DbManager.db.atomic() as transaction:
            try:
                ancestor_vals = cls.__query_vals_of_ancestors(pathway_rels)  
                
                print(ancestor_vals)
                
                while True:
                    vals = ancestor_vals[k:min(k+bulk_size,len(ancestor_vals))]
                    if not len(vals):
                        break
                        
                    PathwayAncestor.insert_many(vals).execute()
                    k = k+bulk_size
            except:
                raise "Aie"
                transaction.rollback()
    
        
        # insert chebi pathways
        from biota.compound import Compound
        chebi_pathways = Reactome.parse_chebi_pathway_to_dict(biodata_dir, kwargs['reactome_chebi_pathways_file'])
        comps = []
        for cpw in chebi_pathways:
            chebi_id = "CHEBI:"+cpw["chebi_id"]
            reactome_pathway_id = cpw["reactome_pathway_id"]

            comp = Compound.get(Compound.chebi_id == chebi_id)
            comp.reactome_patwhay_id = reactome_pathway_id
            comps.append(comp)
            
            if len(comps) >= 500:
                Compound.save_all(comps)
                comps = []
        
        if len(comps):
            Compound.save_all(comps)

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `pwo` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        PathwayAncestor.create_table()

    # -- D --

    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `pwo` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        PathwayAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- S -- 
    
    @classmethod
    def __query_vals_of_ancestors(self, pathway_rels):
        vals = []
        for _pw in pathway_rels:
            try:
                val = {
                        'pathway': Pathway.get(Pathway.reactome_id == _pw["reactome_pathway_id"]).id,
                        'ancestor': Pathway.get(Pathway.reactome_id == _pw["ancestor"]).id 
                    }
                vals.append(val)
            except:
                pass
            
        return(vals)


class PathwayAncestor(PWModel):
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
