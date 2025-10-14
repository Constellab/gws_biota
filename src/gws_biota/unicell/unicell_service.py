

import pickle
from typing import List

import networkx as nx
from gws_biota.src.gws_biota.db.biota_db_manager import BiotaDbManager
from gws_core import BadRequestException, Logger

from ..compound.cofactor import Cofactor
from ..taxonomy.taxonomy import Taxonomy
from .unicell import Unicell


class UnicellService:

    @classmethod
    @BiotaDbManager.transaction()
    def create_unicell_skeleton(cls, tax_id=None):
        """ Create a universal cell """
        from ..reaction.reaction import Reaction

        compound_id_list = []
        reaction_id_list = []
        rhea_edge_map = {}

        page = 1
        nb_items_per_page = 1000
        cofactor_list: List[str] = list(Cofactor.get_factors_as_list())
        graph = nx.Graph()

        if tax_id:
            tax = Taxonomy.get_or_none(Taxonomy.tax_id == tax_id)
            if tax is None:
                raise BadRequestException(f"No taxonomy found with taxonomy id {tax_id}")
        else:
            tax = None

        if tax is None:
            query = Reaction.select().where(Reaction.direction == "UN")
        else:
            query = Reaction.search_by_tax_ids(tax.tax_id).where(Reaction.direction == "UN")
            # query = Reaction.select().where(Reaction.direction == "UN")

        nb_rxn = query.count()
        Logger.info(f"Creating unicell with {nb_rxn} reactions ...")

        while True:
            if tax is None:
                current_query = query.paginate(page, nb_items_per_page)
            else:
                current_query = query.paginate(page, nb_items_per_page)

            if len(current_query) == 0:
                break

            Logger.info(f"Reaction page {page}/{round(nb_rxn/nb_items_per_page)+1} ...")
            for rxn in current_query:
                reaction_id_list.append(rxn.rhea_id)
                eqn = rxn.data["equation"]
                for chebi_id_1 in eqn["substrates"]:
                    if chebi_id_1 in cofactor_list:
                        continue
                    for chebi_id_2 in eqn["products"]:
                        if chebi_id_2 in cofactor_list:
                            continue
                        graph.add_edge(chebi_id_1, chebi_id_2, rhea_id=rxn.rhea_id, dg_prime=1.0)
                        if rxn.rhea_id in rhea_edge_map:
                            rhea_edge_map[rxn.rhea_id].append((chebi_id_1, chebi_id_2))
                        else:
                            rhea_edge_map[rxn.rhea_id] = [(chebi_id_1, chebi_id_2)]

                        compound_id_list.extend([chebi_id_1, chebi_id_2])

            page += 1

        compound_id_list = list(set(compound_id_list))
        uni_cell = Unicell(
            compound_id_list=pickle.dumps(compound_id_list),
            reaction_id_list=pickle.dumps(reaction_id_list),
            rhea_edge_map=pickle.dumps(rhea_edge_map),
            graph=pickle.dumps(graph),
        )

        Logger.info("Done!")

        return uni_cell
