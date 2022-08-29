# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import json
import re

from gws_core import BadRequestException, StringHelper


class BiomassReaction():

    DEFAULT_NAME = "biota"
    SKIP_BIGG_EXCHANGE_REACTIONS = True

    @staticmethod
    def _convert_annotation_list_to_dict(annotation):
        annotation_dict = {}
        if isinstance(annotation, list):
            for annotation_val in annotation:
                k = annotation_val[0]
                v = annotation_val[1]
                if k not in annotation_dict:
                    annotation_dict[k] = []
                if "http" in v:
                    v = v.split("/")[-1]
                annotation_dict[k].append(v)
        return annotation_dict

    @ classmethod
    def extract_biomass_reactions_from_file(cls, file: str) -> list:
        with open(file, 'r', encoding="utf-8") as fp:
            data = json.load(fp)
            return cls.extract_biomass_reactions(data)

    @ classmethod
    def extract_biomass_reactions(cls, data: dict) -> list:
        from ..compound.compound import Compound

        ckey = "compounds" if "compounds" in data else "metabolites"
        compounds = data[ckey]
        reactions = data["reactions"]
        comp_dict = {comp["id"]: comp for comp in compounds}

        biomass_rxns = []
        for rxn in reactions:
            id = rxn["id"]
            name = rxn["name"]
            if not id.startswith("BIOMASS_"):
                continue

            current_biomass_rxn = {
                "id": id,
                "name": name
            }

            eqn_def_prod = []
            eqn_def_subs = []
            prods = {}
            subs = {}

            for comp_id in rxn[ckey]:
                comp = comp_dict[comp_id]
                comp_name = StringHelper.slugify(comp["name"], to_lower=False, snakefy=True)
                comp_annotation = comp["annotation"]
                if isinstance(comp_annotation, list):
                    comp_annotation = cls._convert_annotation_list_to_dict(comp_annotation)
                    chebi_ids = comp_annotation.get("CHEBI")
                else:
                    chebi_ids = comp_annotation.get("chebi")

                if chebi_ids:
                    chebi_id = chebi_ids[0]
                else:
                    chebi_id = comp_id

                stoich = float(rxn[ckey][comp_id])
                if stoich < 0:
                    subs[chebi_id] = str(abs(stoich))
                    eqn_def_subs.append(str(abs(stoich))+" "+str(comp_name))
                elif stoich > 0:
                    prods[chebi_id] = str(stoich)
                    eqn_def_prod.append(str(stoich)+" "+str(comp_name))

            current_biomass_rxn["definition"] = " + ".join(eqn_def_subs) + " = " + " + ".join(eqn_def_prod)
            current_biomass_rxn["equation"] = {"substrates": subs, "products": prods}

            eqn_src_subs = " + ".join([v+" "+k for k, v in subs.items()])
            eqn_src_prods = " + ".join([v+" "+k for k, v in prods.items()])
            current_biomass_rxn["source_equation"] = eqn_src_subs + " = " + eqn_src_prods
            current_biomass_rxn["substrates"] = list(subs.keys())
            current_biomass_rxn["products"] = list(prods.keys())

            biomass_rxns.append(current_biomass_rxn)

        return biomass_rxns
