# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import Logger, transaction
from peewee import chunked

from .._helper.rhea import Rhea
from ..base.base_service import BaseService
from ..compound.compound import Compound
from ..enzyme.enzyme import Enzyme
from ..taxonomy.taxonomy import Taxonomy
from .reaction import (Reaction, ReactionEnzyme, ReactionProduct,
                       ReactionSubstrate)


class ReactionService(BaseService):

    @classmethod
    @transaction()
    def create_reaction_db(cls, biodata_dir=None, **kwargs):
        """
        Creates and fills the `reaction` database

        :param biodata_dir: path to the folder that contain the go.obo file
        :type biodata_dir: str
        :param kwargs: dictionnary that contains all data files names
        :type kwargs: dict
        :returns: None
        :rtype: None
        """

        list_of_reactions = Rhea.parse_reaction_from_file(biodata_dir, kwargs['rhea_reaction_file'])
        cls._create_reactions(list_of_reactions)

        list_of_directions = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea_direction_file'])
        cols = Rhea.get_columns_from_lines(list_of_directions)

        for k in ['UN', 'LR', 'RL', 'BI']:
            cls._update_direction_from_list(cols[k], k)

        biocyc_dbs = ['ecocyc', 'metacyc', 'macie']
        for k in biocyc_dbs:
            xref_ids = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea2'+k+'_file'])
            cls._update_master_and_biocyc_ids_from_rhea2biocyc(xref_ids)

        xref_ids = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea2kegg_reaction_file'])
        cls._update_master_and_id_from_rhea2kegg(xref_ids)

        xref_ids = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea2ec_file'])
        cls._update_master_and_biocyc_ids_from_rhea2ec(xref_ids)

        xref_ids = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea2reactome_file'])
        cls._update_master_and_biocyc_ids_from_rhea2ec(xref_ids)

    @classmethod
    def _create_reactions(cls, list_reaction):
        """
        Creates reactions from a list
        Add reactions-substrates and reaction-products relation in
        reaction_subtrates and reations_products by calling
        _create_substrate_vals_from_data(), _create_product_vals_from_data()

        :type list_reaction: list
        :param list_reaction: list of dictionnaries where each element refers
        to a rhea reaction
        :returns: list of reactions entities
        :rtype: list
        """

        rxn_count = len(list_reaction)
        Logger.info(f"Saving {rxn_count} reactions ...")
        reactions = [Reaction(data=data) for data in list_reaction]
        i = 0
        for reaction_chunk in chunked(reactions, cls.BATCH_SIZE):
            i += 1
            Logger.info(f"... saving reaction chunk {i}/{int(rxn_count/cls.BATCH_SIZE)+1}")
            for react in reaction_chunk:
                if 'entry' in react.data.keys():
                    react.rhea_id = react.data['entry']
                    del react.data['entry']
            Reaction.create_all(reaction_chunk)

        vals = []
        for react in reactions:
            vals.extend(cls._create_substrate_vals_from_data(react))
        ReactionSubstrate.insert_all(vals)

        vals = []
        for react in reactions:
            vals.extend(cls._create_product_vals_from_data(react))
        ReactionProduct.insert_all(vals)

        vals = []
        for react in reactions:
            vals.extend(cls._create_enzymes_vals_and_set_ft_names_from_data(react))
        ReactionEnzyme.insert_all(vals)

        # update reaction tf_names
        Reaction.update_all(reactions, fields=['ft_names', 'ft_tax_ids', 'ft_ec_numbers'])

        return reactions

    @classmethod
    def _create_substrate_vals_from_data(cls, react):
        """
        Set substrates from `data`
        """

        vals = []
        Q = Compound.select().where(Compound.chebi_id << react.data['substrates'])
        for comp in Q:
            # react.substrates.add(comp)
            vals.append({
                'reaction': react.id,
                'compound': comp.id
            })
        return vals

    @classmethod
    def _create_product_vals_from_data(cls, react):
        """
        Set products from `data`
        """

        vals = []
        Q = Compound.select().where(Compound.chebi_id << react.data['products'])
        for comp in Q:
            # react.products.add(comp)
            vals.append({
                'reaction': react.id,
                'compound': comp.id
            })
        return vals

    @classmethod
    def _create_enzymes_vals_and_set_ft_names_from_data(cls, react):
        """
        Set enzymes from `data`
        """

        vals = []
        ft_tax_ids = []
        ft_ec_numbers = []
        if 'enzymes' in react.data:
            Q = Enzyme.select().where(Enzyme.ec_number << react.data['enzymes'])
            ft_names = []
            for enz in Q:
                ft_names.append(enz.ft_names)
                # react.enzymes.add(enz)
                vals.append({
                    'reaction': react.id,
                    'enzyme': enz.id
                })

                ft_ec_numbers.append("EC" + enz.ec_number.replace(".", ""))
                for tax_rank in Taxonomy.get_tax_tree():
                    tax_id = getattr(enz, "tax_"+tax_rank)
                    if tax_id:
                        ft_tax_ids.append("TAX" + tax_id)

            # set ft_names
            ft_names = [react.rhea_id.replace(":", ""), *ft_names]
            react.ft_names = ";".join(ft_names)

            # set ft_tax_ids
            react.ft_tax_ids = ";".join(ft_tax_ids)

            # set ft_ec_numbers
            react.ft_ec_numbers = ";".join(ft_ec_numbers)

        return vals
    # -- U --

    @classmethod
    def _update_master_and_biocyc_ids_from_rhea2ec(cls, list_reaction_infos):
        """
        Get informations about master id and biocyc id of from a :file:`rhea2ec.tsv` file
        update those index if the concerned reaction is in the table

        :type list_reaction_infos: list
        :param list_reaction_infos: list of dictionnaries that contains informations about reactions
        """
        rhea_ids = []
        master_ids = {}
        biocyc_ids = {}
        for dict_ in list_reaction_infos:
            rhea_id = 'RHEA:'+dict_['rhea_id']
            rhea_ids.append(rhea_id)
            master_ids[rhea_id] = dict_['master_id']
            biocyc_ids[rhea_id] = dict_['id']

        reaction_list = []
        # for rhea_id in rhea_ids:
        for chunk in chunked(rhea_ids, cls.BATCH_SIZE):
            query = Reaction.select().where(Reaction.rhea_id << chunk)
            for reaction in query:
                if reaction.rhea_id in biocyc_ids:
                    reaction.append_biocyc_id(biocyc_ids[reaction.rhea_id])
                    reaction_list.append(reaction)
        Reaction.update_all(reaction_list, fields=['biocyc_ids'])

    @classmethod
    def _update_master_and_biocyc_ids_from_rhea2biocyc(cls, list_reaction_infos):
        """
        Get informations about master id and biocyc id of from a :file:`rhea2biocyc.tsv` file
        update those index if the concerned reaction is in the table

        :type list_reaction_infos: list
        :param list_reaction_infos: list of dictionnaries that contains informations about reactions
        """
        rhea_ids = []
        master_ids = {}
        biocyc_ids = {}
        for dict_ in list_reaction_infos:
            rhea_id = 'RHEA:'+dict_['rhea_id']
            rhea_ids.append(rhea_id)
            master_ids[rhea_id] = dict_['master_id']
            biocyc_ids[rhea_id] = dict_['id']

        reaction_list = []
        # for rhea_id in rhea_ids:
        for chunk in chunked(rhea_ids, cls.BATCH_SIZE):
            query = Reaction.select().where(Reaction.rhea_id << chunk)
            for reaction in query:
                has_changed = False
                if reaction.rhea_id in master_ids:
                    reaction.set_master_id(master_ids[reaction.rhea_id])
                    has_changed = True
                if reaction.rhea_id in biocyc_ids:
                    reaction.append_biocyc_id(biocyc_ids[reaction.rhea_id])
                    has_changed = True
                if has_changed:
                    reaction_list.append(reaction)
        Reaction.update_all(reaction_list, fields=['master_id', 'biocyc_ids'])

    @classmethod
    def _update_master_and_id_from_rhea2kegg(cls, list_reaction_infos):
        """
        Get informations about master id and biocyc id of from a :file:`rhea2kegg.tsv` file
        update those index if the concerned reaction is in the table

        :type list_reaction_infos: list
        :param list_reaction_infos: list of dictionnaries that contains informations about reactions
        """
        rhea_ids = []
        master_ids = {}
        kegg_ids = {}
        for dict_ in list_reaction_infos:
            rhea_id = 'RHEA:'+dict_['rhea_id']
            rhea_ids.append(rhea_id)
            master_ids[rhea_id] = dict_['master_id']
            kegg_ids[rhea_id] = dict_['id']

        reaction_list = []
        # for rhea_id in rhea_ids:
        for chunk in chunked(rhea_ids, cls.BATCH_SIZE):
            query = Reaction.select().where(Reaction.rhea_id << chunk)
            for reaction in query:
                has_changed = False
                if reaction.rhea_id in master_ids:
                    reaction.set_master_id(master_ids[reaction.rhea_id])
                    has_changed = True
                if reaction.rhea_id in kegg_ids:
                    reaction.set_kegg_id(kegg_ids[reaction.rhea_id])
                    has_changed = True
                if has_changed:
                    reaction_list.append(reaction)
        Reaction.update_all(reaction_list, fields=['master_id', 'kegg_id'])

    @classmethod
    def _update_direction_from_list(cls, list_direction, direction):
        """
        Get informations about direction of from :file:`rhea.tsv` files and
        update the direction property if the concerned reaction is in the table

        :type list_direction: list
        :param list_direction: list of dictionnaries that contains informations about
        directions of reactions
        :type direction : str
        :param direction : direction of reactions in the file
        """
        rhea_ids = []
        for s in list_direction:
            rhea_ids.append('RHEA:'+s)

        reaction_list = []
        # for rhea_id in rhea_ids:
        for chunk in chunked(rhea_ids, cls.BATCH_SIZE):
            query = Reaction.select().where(Reaction.rhea_id << chunk)
            for reaction in query:
                reaction.set_direction(direction)
                reaction_list.append(reaction)
        Reaction.update_all(reaction_list, fields=['direction'])
