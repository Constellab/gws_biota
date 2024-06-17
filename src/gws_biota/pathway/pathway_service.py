# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import transaction, Logger

from .._helper.reactome import Reactome as ReactomeHelper
from ..base.base_service import BaseService
from .pathway import Pathway, PathwayAncestor
from .pathway_compound import PathwayCompound


class PathwayService(BaseService):

    @classmethod
    @transaction()
    def create_pathway_db(cls, path, pwo_file, reactome_pathways_file, reactome_pathway_relations_file,
                          reactome_chebi_pathways_file):
        """
        Creates and fills the `pwo` database

        :params: path of the files
        :type: str
        :returns: None
        :rtype: None
        """

        # insert patwhays
        pathway_dict = ReactomeHelper.parse_pathways_to_dict(path, reactome_pathways_file)
        pathways = []
        for _pw in pathway_dict:
            pw = Pathway(
                name=_pw["name"],
                reactome_pathway_id=_pw["reactome_pathway_id"],
                data={
                    # "name": _pw["name"],
                    "species": _pw["species"]
                }
            )
            ft_names = [pw.name]
            pw.ft_names = cls.format_ft_names(ft_names)
            pathways.append(pw)
        Pathway.create_all(pathways)

        # insert pathways ancestors
        pathway_rels = ReactomeHelper.parse_pathway_relations_to_dict(
            path, reactome_pathway_relations_file)
        vals = cls.__query_vals_of_ancestors(pathway_rels)
        cls._check_duplicat(vals)
        PathwayAncestor.insert_all(vals)

        # insert chebi pathways
        chebi_pathways = ReactomeHelper.parse_chebi_pathway_to_dict(path, reactome_chebi_pathways_file)
        pathways_comps = []
        for cpw in chebi_pathways:
            chebi_id = "CHEBI:"+cpw["chebi_id"]
            pc = PathwayCompound(
                chebi_id=chebi_id,
                reactome_pathway_id=cpw["reactome_pathway_id"],
                species=cpw["species"]
            )
            pathways_comps.append(pc)
        PathwayCompound.create_all(pathways_comps)

    @classmethod
    def __query_vals_of_ancestors(cls, pathway_rels):
        vals = []
        for _pw in pathway_rels:
            try:
                pathway_id = Pathway.get(Pathway.reactome_pathway_id == _pw["reactome_pathway_id"]).id
                ancestor_id = Pathway.get(Pathway.reactome_pathway_id == _pw["ancestor"]).id
                val = {'pathway': pathway_id, 'ancestor': ancestor_id}
                vals.append(val)
            except:
                pass
        return vals

    @classmethod
    def _check_duplicat(cls, vals):
        seen_combinations = set()
        duplicates = []
        for item in vals:
            combination = (item['pathway'], item['ancestor'])
            if combination in seen_combinations:
                duplicates.append(item)
            else:
                seen_combinations.add(combination)
        if duplicates:
            Logger.info("Duplicates found:")
            for duplicate in duplicates:
                Logger.info(duplicate)
        else:
            Logger.info("No duplicates found.")
