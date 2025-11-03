

from gws_biota.db.biota_db_manager import BiotaDbManager
from gws_core import Logger

from .._helper.ontology import Onto as OntoHelper
from ..base.base_service import BaseService
from .go import GO, GOAncestor


class GOService(BaseService):

    @classmethod
    @BiotaDbManager.transaction()
    def create_go_db(cls, path, go_file):
        """
        Creates and fills the `go` database

        :param path: path of the :file:`go.obo`
        :type path: str
        :param go_file: file that contains data file name
        :type go_file: file
        :returns: None
        :rtype: None
        """

        Logger.info("Loading GO file ...")
        onto_go = OntoHelper.create_ontology_from_file(path, go_file)
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
                val = {'go': go.id, 'ancestor': GO.get(
                    GO.go_id == ancestor).id}
                vals.append(val)
        return (vals)
