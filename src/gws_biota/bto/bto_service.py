# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import transaction

from .._helper.ontology import Onto as OntoHelper
from ..base.base_service import BaseService
from .bto import BTO, BTOAncestor


class BTOService(BaseService):

    @classmethod
    @transaction()
    def create_bto_db(cls, path, bto_file):
        """
        Creates and fills the `bto` database

        :param biodata_dir: path of the :file:`bto.json`
        :type biodata_dir: str
        :param kwargs: dictionnary that contains all data file names
        :type kwargs: dict
        """

        # convert to obo if required
        ontology = OntoHelper.create_ontology_from_file(path, bto_file)
        list_bto = OntoHelper.parse_bto_from_ontology(ontology)
        btos = [BTO(data=dict_) for dict_ in list_bto]
        for bto in btos:
            bto.set_bto_id(bto.data["id"])
            bto.set_name(bto.data["name"])
            ft_names = [bto.data["name"], "BTO" + bto.bto_id.replace("BTO:", "")]
            bto.ft_names = cls.format_ft_names(ft_names)
            del bto.data["id"]
        BTO.create_all(btos)

        vals = []
        for bto in btos:
            val = cls.__build_insert_query_vals_of_ancestors(bto)
            for v in val:
                vals.append(v)
        BTOAncestor.insert_all(vals)

    @classmethod
    def __build_insert_query_vals_of_ancestors(self, bto):
        """
        Look for the bto term ancestors and returns all bto-bto_ancetors relations in a list.

        :returns: a list of dictionnaries inf the following format: {'bto': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        if 'ancestors' not in bto.data:
            return vals
        for ancestor in bto.data['ancestors']:
            if ancestor != bto.bto_id:
                ancestors = BTO.select(BTO.id).where(BTO.bto_id == ancestor)
                if len(ancestors) > 0:
                    val = {'bto': bto.id, 'ancestor': ancestors[0].id}
                    vals.append(val)
        return vals
