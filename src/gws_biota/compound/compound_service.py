# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import math

from gws_core import transaction

from .._helper.chebi import Chebi as ChebiHelper
from ..compound.compound import Compound, CompoundAncestor
from ..base.base_service import BaseService

class CompoundService(BaseService):

    @staticmethod
    def _to_float(val):
        try:
            val = float(val)
        except Exception as _:
            return None
        if math.isnan(val):
            val = None
        return val

    @classmethod
    @transaction()
    def create_compound_db(cls, biodata_dir=None, **kwargs):
        """
        Creates and fills the `chebi_ontology` database

        :type biodata_dir: str
        :param biodata_dir: path of the :file:`chebi.obo`
        :type kwargs: dict
        :param kwargs: dictionnary that contains all data files names
        :returns: None
        :rtype: None
        """

        data_dir, corrected_file_name = ChebiHelper.correction_of_chebi_file(biodata_dir, kwargs['chebi_file'])
        onto = ChebiHelper.create_ontology_from_file(data_dir, corrected_file_name)
        list_chebi = ChebiHelper.parse_onto_from_ontology(onto)
        compounds = [Compound(data=dict_) for dict_ in list_chebi]
        for comp in compounds:
            comp.set_name(comp.data["name"])
            comp.chebi_id = comp.data["id"]
            comp.formula = comp.data["formula"]
            comp.inchi = comp.data["inchi"]
            comp.inchikey = comp.data["inchikey"]
            comp.smiles = comp.data["smiles"]
            if not comp.data["mass"] is None:
                comp.mass = cls._to_float(comp.data["mass"])
            if not comp.data["monoisotopic_mass"] is None:
                comp.monoisotopic_mass = cls._to_float(comp.data["monoisotopic_mass"])
            if not comp.data["charge"] is None:
                comp.charge = cls._to_float(comp.data["charge"])
            comp.chebi_star = comp.data["subsets"]
            if "kegg" in comp.data["xref"]:
                comp.kegg_id = comp.data["xref"]["kegg"]
                del comp.data["xref"]["kegg"]
            if "metacyc" in comp.data["xref"]:
                comp.metacyc_id = comp.data["xref"]["metacyc"]
                del comp.data["xref"]["metacyc"]

            all_ids = [comp.chebi_id, *comp.alt_chebi_ids]
            if comp.kegg_id is not None:
                all_ids.append(comp.kegg_id)
            all_ids_trimed = [ elt.replace("CHEBI:", "") for elt in all_ids ]            
            comp.ft_names=";".join(list(set([ comp.data["name"], *all_ids_trimed])))

            del comp.data["id"]
            del comp.data["inchi"]
            del comp.data["formula"]
            del comp.data["inchikey"]
            del comp.data["smiles"]
            del comp.data["mass"]
            del comp.data["monoisotopic_mass"]
            del comp.data["charge"]
            del comp.data["subsets"]
        Compound.save_all(compounds)

        # save ancestors
        vals = []
        for compound in compounds:
            val = cls._get_ancestors_query(compound)
            for v in val:
                vals.append(v)
            if len(vals) >= cls.BULK_SIZE:
                CompoundAncestor.insert_many(vals).execute()
                vals = []
        if len(vals):
            CompoundAncestor.insert_many(vals).execute()
            vals = []
 
        # # save alternatives
        # vals = []
        # for compound in compounds:
        #     if 'alt_id' in compound.data:
        #         alt_ids = compound.data['alt_id']
        #         for c_id in alt_ids:
        #             c = CompoundAlternative(main_compound_chebi_id=compound.id, alt_compound_chebi_id=c_id)
        #             vals.append(c)
        #     if len(vals) >= cls.BULK_SIZE:
        #         CompoundAlternative.save_all(vals)
        #         vals = []
        # if len(vals):
        #     CompoundAlternative.save_all(vals)
        #     vals = []

    @classmethod
    def _get_ancestors_query(cls, compound):
        """
        Look for the compound term ancestors and returns all ancetors relations in a list

        :returns: a list of dictionnaries inf the following format: {'compound': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        if 'ancestors' not in compound.data:
            return vals
        for ancestor in compound.data['ancestors']:
            if ancestor != compound.chebi_id :
                val = {'compound': compound.id, 'ancestor': Compound.get(
                    Compound.chebi_id == ancestor).id}
                vals.append(val)
        return vals
