# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
import pickle

import numpy
from gws_core import Logger, transaction
from scipy import sparse

from ..compound.compound_layout import CompoundLayout
from .unicell import Unicell


class UnicellService:

    @classmethod
    @transaction()
    def create_unicell_db(cls, biodata_dir=None, **kwargs):
        from ..compound.compound import Compound
        from ..reaction.reaction import Reaction

        nb_comps = Compound.select().count()
        nb_rxn = Reaction.select().where(Reaction.direction == "UN").count()

        Logger.info(f"Data size: ({nb_comps}, {nb_rxn})")

        flat_layout = CompoundLayout.get_flat_data()

        compound_id_list = []
        compound_x_list = []
        compound_y_list = []

        #compound_name_list = []
        reaction_id_list = []
        #reaction_name_list = []
        #reaction_ec_list = []
        stochiometric_matrix = numpy.zeros([nb_comps, nb_rxn], dtype=numpy.int8)

        page = 1
        nb_items_per_page = 1000
        while True:
            Q = Reaction.select().where(Reaction.direction == "UN").paginate(page, nb_items_per_page)
            if len(Q) == 0:
                break

            Logger.info(f"Reaction page {page}/{round(nb_rxn/nb_items_per_page)+1} ...")
            for rxn in Q:
                rxn_count = len(reaction_id_list)
                reaction_id_list.append(rxn.rhea_id)
                # reaction_name_list.append(rxn.name)
                # reaction_ec_list.append(rxn.ec_number)
                eqn = rxn.data["equation"]

                # create stochiometric_matrix
                for chebi_id in eqn["substrates"]:
                    if chebi_id not in compound_id_list:
                        comp_count = len(compound_id_list)
                        compound_id_list.append(chebi_id)
                        layout = CompoundLayout.get_layout_by_chebi_id(synonym_chebi_ids=chebi_id)
                        compound_x_list.append(layout["x"])
                        compound_y_list.append(layout["y"])
                        # compound_cluster_list = layout["cluster"]
                        # compound_name_list.append(name)
                        stoich = eqn["substrates"][chebi_id]
                        stochiometric_matrix[comp_count, rxn_count] = -int(stoich)

                for chebi_id in eqn["products"]:
                    if chebi_id not in compound_id_list:
                        comp_count = len(compound_id_list)
                        compound_id_list.append(chebi_id)
                        layout = CompoundLayout.get_layout_by_chebi_id(synonym_chebi_ids=chebi_id)
                        compound_x_list.append(layout["x"])
                        compound_y_list.append(layout["y"])
                        # compound_cluster_list = layout["cluster"]
                        # compound_name_list.append(name)
                        stoich = eqn["products"][chebi_id]
                        stochiometric_matrix[comp_count, rxn_count] = int(stoich)

            page += 1

        numpy.fill_diagonal(stochiometric_matrix, 0)

        # remove unconnected compounds
        Logger.info("Removing unconneted compounds ...")
        nz_idx = ~numpy.all(stochiometric_matrix == 0, axis=1)
        stochiometric_matrix = stochiometric_matrix[nz_idx]
        stochiometric_matrix = sparse.csr_array(stochiometric_matrix)
        Logger.info(f"Data size: {stochiometric_matrix.shape}")
        compound_id_list = [compound_id_list[i] for i in range(0, len(nz_idx)) if nz_idx[i]]

        # sort by position
        # x = numpy.array(compound_x_list)
        # sort_x_index = numpy.argsort(x).tolist()
        # y = numpy.array(compound_y_list)
        # sort_y_index = numpy.argsort(y).tolist()

        # print(len(comp_index_to_chebi))
        # print(len(compound_id_list))
        # Logger.info(f"Size of comp_index_to_chebi {len(comp_index_to_chebi)} ...")
        # Logger.info(f"Size of compound_id_list {len(compound_id_list)} ...")

        uc = Unicell(
            compound_id_list=pickle.dumps(compound_id_list),
            reaction_id_list=pickle.dumps(reaction_id_list),
            stochiometric_matrix=pickle.dumps(stochiometric_matrix),
        )
        uc.save()

        return uc
