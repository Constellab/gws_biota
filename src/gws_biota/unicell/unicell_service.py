# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import numpy
import os
from gws_core import transaction
from .unicell import Unicell

class UnicellService:
    
    @classmethod
    @transaction()
    def create_unicell_db(cls, biodata_dir = None, **kwargs):
        from ..reaction.reaction import Reaction

        nb_comps = Compound.select().count()
        nb_rxn = Reaction.select().count()
        

        rxn_ids = {}
        comp_ids = {}
        rxn_ids_map = {}
        comp_ids_map = {}

        graph_comp2rxn = numpy.zeros([nb_comps, nb_rxn], dtype=int)
        graph_comp2comp = numpy.zeros([nb_comps, nb_comps], dtype=int)

        
        page = 1
        while True:
            Q = Reaction.select().paginate(page, 500)
            if not len(Q):
                return
            for rxn in Q:
                rxn_count = len(rxn_ids)
                rxn_ids[rxn_count] = rxn.rhea_id

                eqn = rxn.data["equation"]
                all_chebis = []
                for chebi_id in eqn["substrates"]:
                    if chebi_id not in comp_ids.value():
                        comp_count = len(comp_ids)
                        comp_ids[comp_count] = compound.chebi_id
                        stoich = eqn["substrates"][chebi_id]
                        graph_comp2rxn[comp_count, rxn_count] = -int(stoich)
                        all_chebis.append(chebi_id)

                for chebi_id in eqn["products"]:
                    if chebi_id not in comp_ids.value():
                        comp_count = len(comp_ids)
                        comp_ids[comp_count] = compound.chebi_id
                        stoich = eqn["products"][chebi_id]
                        graph_comp2rxn[comp_count, rxn_count] = int(stoich)
                        all_chebis.append(chebi_id)

                for chebi_id in all_chebis:
                    
                    graph_comp2comp[comp_count, rxn_count] = int(stoich)
                
                    