# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import transaction
from .._helper.ontology import Onto as OntoHelper
from ..eco.eco import ECO, ECOAncestor
from ..base.base_service import BaseService

class ECOService(BaseService):

    @classmethod
    @transaction()
    def create_eco_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `eco` database
        
        :param biodata_dir: path of the :file:`eco.obo`
        :type biodata_dir: str
        :param kwargs: dictionnary that contains all data files names
        :type kwargs: dict
        :returns: None
        :rtype: None
        """
        
        data_dir, corrected_file_name = OntoHelper.correction_of_eco_file(biodata_dir, kwargs['eco_file'])
        onto_eco = OntoHelper.create_ontology_from_obo(data_dir, corrected_file_name)
        list_eco = OntoHelper.parse_eco_terms_from_ontoloy(onto_eco)
        ecos = [ECO(data = dict_) for dict_ in list_eco]
        for eco in ecos:
            eco.set_eco_id( eco.data["id"] )
            eco.set_name( eco.data["name"] )
            eco.ft_names=";".join(list(set([ eco.data["name"], eco.eco_id.replace("ECO:", "")]))),
            del eco.data["id"]
        ECO.save_all(ecos)
        
        vals = []
        for eco in ecos:
            val = cls._get_ancestors_query(eco)
            for v in val:
                vals.append(v)
            if len(vals) >= cls.BULK_SIZE:
                ECOAncestor.insert_many(vals).execute()
                vals = []
        if len(vals) != 0:
            ECOAncestor.insert_many(vals).execute()
            vals = []

    # -- G --

    @classmethod
    def _get_ancestors_query(cls, eco):
        """
        Look for the eco term ancestors and returns all eco-eco_ancetors relations in a list 

        :returns: a list of dictionnaries inf the following format: {'eco': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        if 'ancestors' not in eco.data:
            return vals
        for ancestor in eco.data['ancestors']:
            if ancestor != eco.eco_id:
                val = {'eco': eco.id, 'ancestor': ECO.get(ECO.eco_id == ancestor).id }
                vals.append(val)
        return(vals)
