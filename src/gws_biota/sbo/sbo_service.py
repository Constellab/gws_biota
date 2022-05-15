# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import transaction
from .._helper.ontology import Onto as OntoHelper
from .sbo import SBO, SBOAncestor

class SBOService:
    
    @classmethod
    @transaction()
    def create_sbo_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `sbo` database

        :param biodata_dir: path to the folder that contain the :file:`sbo.obo` file
        :type biodata_dir: str
        :param files_test: dictionnary that contains all data files names
        :type files_test: dict
        :returns: None
        :rtype: None
        """

        data_dir, corrected_file_name = OntoHelper.correction_of_sbo_file(biodata_dir, kwargs['sbo_file'])
        ontology = OntoHelper.create_ontology_from_obo(data_dir, corrected_file_name)
        list_sbo = OntoHelper.parse_sbo_terms_from_ontology(ontology)
        sbos = [SBO(data = dict_) for dict_ in list_sbo]
        for sbo in sbos:
            sbo.set_sbo_id(sbo.data["id"])
            sbo.set_name(sbo.data["name"])
            del sbo.data["id"]
        SBO.save_all(sbos)
        vals = []
        bulk_size = 100
        for sbo in sbos:
            if 'ancestors' in sbo.data.keys():
                val = cls.__build_insert_query_vals_of_ancestors(sbo)
                if len(val) != 0:
                    for v in val:
                        vals.append(v)
                        if len(vals) == bulk_size:
                            SBOAncestor.insert_many(vals).execute()
                            vals = []
                    
                    if len(vals) != 0:
                        SBOAncestor.insert_many(vals).execute()
                        vals = []
    
    @classmethod
    def __build_insert_query_vals_of_ancestors(cls, sbo):
        """
        Look for the sbo term ancestors and returns all sbo-sbo_ancestors relations in a list.

        :returns: a list of dictionnaries inf the following format: {'sbo': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        if 'ancestors' not in sbo.data:
            return vals
        for ancestor in sbo.data['ancestors']:
            if(ancestor != sbo.sbo_id):
                val = {'sbo': sbo.id, 'ancestor': SBO.get(SBO.sbo_id == ancestor).id }
                vals.append(val)
        return(vals)
