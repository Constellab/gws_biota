# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import transaction
from .._helper.ontology import Onto as OntoHelper
from .bto import BTO, BTOAncestor

class BTOService:
    
    @classmethod
    @transaction()
    def create_bto_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `bto` database

        :param biodata_dir: path of the :file:`bto.json`
        :type biodata_dir: str
        :param kwargs: dictionnary that contains all data file names
        :type kwargs: dict
        """

        list_bto = OntoHelper.parse_bto_from_json(biodata_dir, kwargs['bto_file'])
        btos = [BTO(data = dict_) for dict_ in list_bto]
        for bto in btos:
            bto.set_bto_id( bto.data["id"] )
            bto.set_name( bto.data["name"] )
            del bto.data["id"]
        BTO.save_all(btos)
        vals = []
        bulk_size = 100
        for bto in btos:
            val = cls.__build_insert_query_vals_of_ancestors(bto)
            if len(val):
                for v in val:
                    vals.append(v)
                    if len(vals) == bulk_size:
                        BTOAncestor.insert_many(vals).execute()
                        vals = []
                if len(vals) != 0:
                    BTOAncestor.insert_many(vals).execute()
                    vals = []

    @classmethod
    def __build_insert_query_vals_of_ancestors(self, bto):
        """
        Look for the bto term ancestors and returns all bto-bto_ancetors relations in a list.

        :returns: a list of dictionnaries inf the following format: {'bto': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        for i in range(0,len(bto.data['ancestors'])):
            if (bto.data['ancestors'][i] != bto.bto_id):
                ancestors = BTO.select(BTO.id).where(BTO.bto_id == bto.data['ancestors'][i])
                if ancestors:
                    val = {'bto': bto.id, 'ancestor': ancestors[0].id }
                    vals.append(val)
        return vals
        