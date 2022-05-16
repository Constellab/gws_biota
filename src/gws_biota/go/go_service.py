# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField

from gws_core import transaction
from ..db.db_manager import DbManager
from ..base.base import Base
from ..ontology.ontology import Ontology
from .._helper.ontology import Onto as OntoHelper
from .go import GO, GOAncestor

class GOService:

    @classmethod
    @transaction()
    def create_go_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `go` database

        :param biodata_dir: path of the :file:`go.obo`
        :type biodata_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """

        onto_go = OntoHelper.create_ontology_from_obo(biodata_dir, kwargs['go_file'])
        list_go = OntoHelper.parse_obo_from_ontology(onto_go)
        gos = [GO(data = dict_) for dict_ in list_go]
        for go in gos:
            go.set_go_id(go.data["id"])
            go.set_name(go.data["name"])
            go.set_namespace(go.data["namespace"])
            del go.data["id"]
        GO.save_all(gos)
        vals = []
        bulk_size = 500
        for go in gos:
            if 'ancestors' in go.data.keys():
                val = cls.__build_insert_query_vals_of_ancestors(go)
                for v in val:
                    vals.append(v)
            if len(vals) >= bulk_size:
                GOAncestor.insert_many(vals).execute()
                vals = []
        if len(vals):
            GOAncestor.insert_many(vals).execute()
            vals = []
    
    @classmethod
    def __build_insert_query_vals_of_ancestors(self, go):
        """
        Look for the go term ancestors and returns all go-go_ancestors relations in a list 

        :returns: A list of dictionnaries in the following format: {'go': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        if 'ancestors' not in go.data:
            return vals
        for ancestor in go.data['ancestors']:
            if ancestor != go.go_id:
                val = {'go': go.id, 'ancestor': GO.get(GO.go_id == ancestor).id }
                vals.append(val)
        return(vals)
