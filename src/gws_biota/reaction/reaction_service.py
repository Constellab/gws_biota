# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import chunked

from gws_core import transaction, Logger
from .._helper.rhea import Rhea
from ..compound.compound import Compound
from .reaction import Reaction, ReactionSubstrate, ReactionProduct, ReactionEnzyme
from ..enzyme.enzyme import Enzyme
from ..base.base_service import BaseService

class ReactionService(BaseService):
    
    @classmethod
    @transaction()
    def create_reaction_db(cls, biodata_dir = None, **kwargs):
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
        cls.__create_reactions(list_of_reactions)
        
        list_of_directions = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea_direction_file'])
        cols = Rhea.get_columns_from_lines(list_of_directions)

        for k in ['UN', 'LR', 'RL', 'BI']:
            cls.__update_direction_from_list(cols[k], k)

        biocyc_dbs = ['ecocyc', 'metacyc', 'macie']
        for k in biocyc_dbs:
            xref_ids = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea2'+k+'_file'])
            cls.__update_master_and_biocyc_ids_from_rhea2biocyc(xref_ids)
        
        xref_ids = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea2kegg_reaction_file'])
        cls.__update_master_and_id_from_rhea2kegg(xref_ids)
        
        xref_ids = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea2ec_file'])
        cls.__update_master_and_biocyc_ids_from_rhea2ec(xref_ids)
        
        xref_ids = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea2reactome_file'])
        cls.__update_master_and_biocyc_ids_from_rhea2ec(xref_ids)

    @classmethod
    def __create_reactions(cls, list_reaction):
        """
        Creates reactions from a list
        Add reactions-substrates and reaction-products relation in
        reaction_subtrates and reations_products by calling
        __create_substrate_vals_from_data(), __create_product_vals_from_data()

        :type list_reaction: list
        :param list_reaction: list of dictionnaries where each element refers 
        to a rhea reaction
        :returns: list of reactions entities
        :rtype: list
        """

        rxn_count = len(list_reaction)
        Logger.info(f"Saving {rxn_count} reactions ...")

        i = 0
        for chunk in chunked(list_reaction, cls.BATCH_SIZE):
            i += 1
            reactions = [Reaction(data = data) for data in chunk]
            Logger.info(f"... saving reaction chunk {i}/{int(rxn_count/cls.BATCH_SIZE)+1}")
            for react in reactions:
                if 'entry' in react.data.keys():
                    react.rhea_id = react.data['entry']
                    del react.data['entry']
            Reaction.create_all(reactions)
        
        vals = []
        for react in reactions:
            vals.extend(cls.__create_substrate_vals_from_data(react))
        ReactionSubstrate.insert_all(vals)

        vals = []
        for react in reactions:
            vals.extend(cls.__create_product_vals_from_data(react))
        ReactionProduct.insert_all(vals)

        vals = []
        for react in reactions:
            vals.extend(cls.__create_enzymes_vals_and_set_ft_names_from_data(react))
        ReactionEnzyme.insert_all(vals)
        
        # update reaction tf_names
        Reaction.update_all(reactions, fields=['ft_names'])

        return reactions

    @classmethod
    def __create_substrate_vals_from_data(cls, react):
        """
        Set substrates from `data`
        """

        vals = []
        Q = Compound.select().where(Compound.chebi_id << react.data['substrates'])
        for comp in Q:
            #react.substrates.add(comp)
            vals.append({
                'reaction': react.id,
                'compound': comp.id
            })
        return vals
    
    @classmethod
    def __create_product_vals_from_data(cls, react):
        """
        Set products from `data`
        """

        vals = []
        Q = Compound.select().where(Compound.chebi_id << react.data['products'])
        for comp in Q:
            #react.products.add(comp)
            vals.append({
                'reaction': react.id,
                'compound': comp.id
            })
        return vals

    @classmethod
    def __create_enzymes_vals_and_set_ft_names_from_data(cls, react):
        """
        Set enzymes from `data`
        """
        
        vals = []
        if 'enzymes' in react.data:
            Q = Enzyme.select().where(Enzyme.ec_number << react.data['enzymes'])
            tab = []
            for enz in Q:
                tab.append( enz.ft_names )
                #react.enzymes.add(enz)
                vals.append({
                    'reaction': react.id,
                    'enzyme': enz.id
                })
            react.ft_names = cls.format_ft_names(tab)
        return vals
    # -- U --

    @classmethod
    def __update_master_and_biocyc_ids_from_rhea2ec(cls, list_reaction_infos):
        """
        Get informations about master id and biocyc id of from a :file:`rhea2ec.tsv` file
        update those index if the concerned reaction is in the table

        :type list_reaction_infos: list
        :param list_reaction_infos: list of dictionnaries that contains informations about reactions
        """
        rhea_ids = []
        master_ids = {}
        biocyc_ids = {}
        for dict__ in list_reaction_infos:
            rhea_id = 'RHEA:'+dict__['rhea_id']
            rhea_ids.append(rhea_id)
            master_ids[rhea_id] = dict__['master_id']
            biocyc_ids[rhea_id] = dict__['id']

        reaction_list = []
        #for rhea_id in rhea_ids:
        for chunk in chunked(rhea_ids, cls.BATCH_SIZE):
            query = Reaction.select().where(Reaction.rhea_id << chunk)
            for reaction in query:
                if reaction.rhea_id in biocyc_ids:
                    reaction.append_biocyc_id(biocyc_ids[reaction.rhea_id])
                    reaction_list.append(reaction)
        Reaction.update_all(reaction_list, fields=['biocyc_ids'])

    @classmethod
    def __update_master_and_biocyc_ids_from_rhea2biocyc(cls, list_reaction_infos):
        """
        Get informations about master id and biocyc id of from a :file:`rhea2biocyc.tsv` file
        update those index if the concerned reaction is in the table

        :type list_reaction_infos: list
        :param list_reaction_infos: list of dictionnaries that contains informations about reactions
        """
        rhea_ids = []
        master_ids = {}
        biocyc_ids = {}
        for dict__ in list_reaction_infos:
            rhea_id = 'RHEA:'+dict__['rhea_id']
            rhea_ids.append(rhea_id)
            master_ids[rhea_id] = dict__['master_id']
            biocyc_ids[rhea_id] = dict__['id']
        
        reaction_list = []
        #for rhea_id in rhea_ids:
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

        # start = 0
        # stop = start + cls.BATCH_SIZE
        # while True:
        #     if start >= len(rhea_ids):
        #         break
        #     q = Reaction.select().where(Reaction.rhea_id << rhea_ids[start:stop])
        #     for reaction in q:
        #         if reaction.rhea_id in master_ids:
        #             reaction.set_master_id(master_ids[reaction.rhea_id])
        #         if reaction.rhea_id in biocyc_ids:
        #             reaction.append_biocyc_id(biocyc_ids[reaction.rhea_id])
        #     start = stop
        #     stop += cls.BATCH_SIZE
        #     Reaction.update_all(q, fields=['master_id', 'biocyc_ids'])

    @classmethod
    def __update_master_and_id_from_rhea2kegg(cls, list_reaction_infos):
        """
        Get informations about master id and biocyc id of from a :file:`rhea2kegg.tsv` file
        update those index if the concerned reaction is in the table

        :type list_reaction_infos: list
        :param list_reaction_infos: list of dictionnaries that contains informations about reactions
        """
        rhea_ids = []
        master_ids = {}
        kegg_ids = {}
        for dict__ in list_reaction_infos:
            rhea_id = 'RHEA:'+dict__['rhea_id']
            rhea_ids.append(rhea_id)
            master_ids[rhea_id] = dict__['master_id']
            kegg_ids[rhea_id] = dict__['id']
        
        reaction_list = []
        #for rhea_id in rhea_ids:
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

        # start = 0
        # stop = cls.BATCH_SIZE
        # while True:
        #     if start >= len(rhea_ids):
        #         break
        #     q = Reaction.select().where(Reaction.rhea_id << rhea_ids[start:stop])
        #     for reaction in q:
        #         if reaction.rhea_id in master_ids:
        #             reaction.set_master_id(master_ids[reaction.rhea_id])
        #         if reaction.rhea_id in kegg_ids:
        #             reaction.set_kegg_id(kegg_ids[reaction.rhea_id])
        #     start = stop
        #     stop += cls.BATCH_SIZE
        #     Reaction.update_all(q, fields=['master_id', 'kegg_id'])

    @classmethod
    def __update_direction_from_list(cls, list_direction, direction):
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
        #for rhea_id in rhea_ids:
        for chunk in chunked(rhea_ids, cls.BATCH_SIZE):
            query = Reaction.select().where(Reaction.rhea_id << chunk)
            for reaction in query:
                reaction.set_direction(direction)
                reaction_list.append(reaction)
        Reaction.update_all(reaction_list, fields=['direction'])

        # start = 0
        # stop = cls.BATCH_SIZE
        # while True:
        #     if start >= len(rhea_ids):
        #         break
        #     q = Reaction.select().where(Reaction.rhea_id << rhea_ids[start:stop])
        #     for reaction in q:
        #         reaction.set_direction(direction)
        #     start = stop
        #     stop += cls.BATCH_SIZE
        #     Reaction.update_all(q, fields=['direction'])
