

from gws_core import Logger

from gws_biota.db.biota_db_manager import BiotaDbManager

from .._helper.ontology import Onto as OntoHelper
from ..base.base_service import BaseService
from ..eco.eco import ECO, ECOAncestor


class ECOService(BaseService):

    @classmethod
    @BiotaDbManager.transaction()
    def create_eco_db(cls, path, eco_file):
        """
        Creates and fills the `eco` database

        :param path: path of the :file:`eco.obo`
        :type path: str
        :param eco_file: file that contains data file name
        :type eco_file: file
        :returns: None
        :rtype: None
        """

        data_dir, corrected_file_name = OntoHelper.correction_of_eco_file(
            path, eco_file)
        Logger.info(f"tuple : {data_dir}, {corrected_file_name}")

        onto_eco = OntoHelper.create_ontology_from_file(
            data_dir, corrected_file_name)

        list_eco = OntoHelper.parse_eco_terms_from_ontoloy(onto_eco)
        ecos = [ECO(data=dict_) for dict_ in list_eco]
        for eco in ecos:
            eco.set_eco_id(eco.data["id"])
            eco.set_name(eco.data["name"])
            ft_names = [eco.data["name"], "ECO" +
                        eco.eco_id.replace("ECO:", "")]
            eco.ft_names = cls.format_ft_names(ft_names)
            del eco.data["id"]
        ECO.create_all(ecos)

        vals = []
        for eco in ecos:
            val = cls._get_ancestors_query(eco)
            for v in val:
                vals.append(v)
        ECOAncestor.insert_all(vals)

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
                val = {'eco': eco.id, 'ancestor': ECO.get(
                    ECO.eco_id == ancestor).id}
                vals.append(val)
        return (vals)
