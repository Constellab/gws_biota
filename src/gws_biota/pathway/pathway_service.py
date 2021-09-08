# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import transaction
from .._helper.reactome import Reactome as ReactomeHelper
from .pathway import Pathway, PathwayAncestor
from .pathway_compounds import PathwayCompounds

class PathwayService:
    
    @classmethod
    @transaction()
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
        
        # insert patwhays
        pathway_dict = ReactomeHelper.parse_pathways_to_dict(biodata_dir, kwargs['reactome_pathways_file'])
        pathways = []
        for _pw in pathway_dict:
            pw = Pathway(
                name = _pw["name"],
                reactome_pathway_id = _pw["reactome_pathway_id"],
                data = {
                    #"name": _pw["name"],
                    "species": _pw["species"]
                }
            )
            pathways.append(pw)
        Pathway.save_all(pathways)

        # insert pathways ancestors
        pathway_rels = ReactomeHelper.parse_pathway_relations_to_dict(biodata_dir, kwargs['reactome_pathway_relations_file'])      
        k = 0
        bulk_size = 100
        ancestor_vals = cls.__query_vals_of_ancestors(pathway_rels)  
        while True:
            vals = ancestor_vals[k:min(k+bulk_size,len(ancestor_vals))]
            if not len(vals):
                break
            PathwayAncestor.insert_many(vals).execute()
            k = k+bulk_size
    
        
        # insert chebi pathways
        chebi_pathways = ReactomeHelper.parse_chebi_pathway_to_dict(biodata_dir, kwargs['reactome_chebi_pathways_file'])
        pathways_comps = []
        for cpw in chebi_pathways:
            chebi_id = "CHEBI:"+cpw["chebi_id"]
            pc = PathwayCompounds(
                chebi_id = chebi_id, 
                reactome_pathway_id = cpw["reactome_pathway_id"],
                species = cpw["species"]
            )
            pathways_comps.append(pc)
            if len(pathways_comps) >= 500:
                PathwayCompounds.save_all(pathways_comps)
                pathways_comps = []
        if len(pathways_comps):
            PathwayCompounds.save_all(pathways_comps)

    @classmethod
    def __query_vals_of_ancestors(self, pathway_rels):
        vals = []
        for _pw in pathway_rels:
            try:
                val = {
                        'pathway': Pathway.get(Pathway.reactome_pathway_id == _pw["reactome_pathway_id"]).id,
                        'ancestor': Pathway.get(Pathway.reactome_pathway_id == _pw["ancestor"]).id 
                    }
                vals.append(val)
            except:
                pass
        return(vals)
