# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import Logger, transaction
from peewee import CharField, ForeignKeyField

from .._helper.ontology import Onto as OntoHelper
from ..base.base import Base
from ..base.base_service import BaseService
from ..db.db_manager import DbManager
from ..ontology.ontology import Ontology
from .go import GO, GOAncestor


class GOService(BaseService):

    @classmethod
    @transaction()
    def create_go_db(cls, biodata_dir=None, **kwargs):
        """
        Creates and fills the `go` database

        :param biodata_dir: path of the :file:`go.obo`
        :type biodata_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """

        Logger.info("Loading GO file ...")
        onto_go = OntoHelper.create_ontology_from_obo(biodata_dir, kwargs['go_file'])
        list_go = OntoHelper.parse_obo_from_ontology(onto_go)
        gos = [GO(data=dict_) for dict_ in list_go]

        Logger.info("Saving GO terms ...")
        for go in gos:
            go.set_go_id(go.data["id"])
            go.set_name(go.data["name"])
            go.set_namespace(go.data["namespace"])

            ft_names = [go.data["name"], go.data["id"].replace(":", "")]
            go.ft_names = cls.format_ft_names(ft_names)

            del go.data["id"]
        GO.create_all(gos)

        Logger.info("Saving GO ancestors ...")
        vals = []
        for go in gos:
            val = cls.__build_insert_query_vals_of_ancestors(go)
            for v in val:
                vals.append(v)
        GOAncestor.insert_all(vals)

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
                val = {'go': go.id, 'ancestor': GO.get(GO.go_id == ancestor).id}
                vals.append(val)
        return (vals)
