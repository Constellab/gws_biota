# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import transaction
from .._helper.rhea import Rhea
from ..compound.compound import Compound
from .reaction import Reaction
from ..enzyme.enzyme import Enzyme

class ReactionService:
    
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
            cls.__update_master_and_id_from_rhea2biocyc(xref_ids)
        xref_ids = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea2kegg_reaction_file'])
        cls.__update_master_and_id_from_rhea2kegg(xref_ids)
        xref_ids = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea2ec_file'])
        cls.__update_master_and_id_from_rhea2ec(xref_ids)
        xref_ids = Rhea.parse_csv_from_file(biodata_dir, kwargs['rhea2reactome_file'])
        cls.__update_master_and_id_from_rhea2ec(xref_ids)

    @classmethod
    def __create_reactions(cls, list_reaction):
        """
        Creates reactions from a list
        Add reactions-substrates and reaction-products relation in
        reaction_subtrates and reations_products by calling
        __set_substrates_from_data(), __set_products_from_data()

        :type list_reaction: list
        :param list_reaction: list of dictionnaries where each element refers 
        to a rhea reaction
        :returns: list of reactions entities
        :rtype: list
        """
        reactions = [Reaction(data = dict) for dict in list_reaction]
        for react in reactions:
            if 'entry' in react.data.keys():
                react.rhea_id = react.data['entry']
                del react.data['entry']
        Reaction.save_all(reactions)
        for react in reactions:
            cls.__set_substrates_from_data(react)
            cls.__set_products_from_data(react)
            if 'enzymes' in react.data.keys():
                cls.__set_enzymes_from_data(react)
        Reaction.save_all(reactions)
        return reactions

    @classmethod
    def __set_substrates_from_data(self, react):
        """
        Set substrates from `data`
        """
        Q = Compound.select().where(Compound.chebi_id << react.data['substrates'])
        for comp in Q:
            react.substrates.add(comp)
    
    @classmethod
    def __set_products_from_data(self, react):
        """
        Set products from `data`
        """
        Q = Compound.select().where(Compound.chebi_id << react.data['products'])
        for comp in Q:
            react.products.add(comp)
    
    @classmethod
    def __set_enzymes_from_data(self, react):
        """
        Set enzymes from `data`
        """
        
        Q = Enzyme.select().where(Enzyme.ec_number << react.data['enzymes'])
        tab = []
        for enz in Q:
            tab.append( enz.ft_names )
            react.enzymes.add(enz)
        react.ft_names = ",".join(tab)
    # -- U --

    @classmethod
    def __update_master_and_id_from_rhea2ec(cls, list_reaction_infos):
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
        bulk_size = 750
        start = 0
        stop = start + bulk_size
        while True:
            if start >= len(rhea_ids):
                break
            Q = Reaction.select().where(Reaction.rhea_id << rhea_ids[start:stop])
            for reaction in Q:
                if reaction.rhea_id in biocyc_ids:
                    reaction.append_biocyc_id(biocyc_ids[reaction.rhea_id])
            start = stop
            stop = start + bulk_size
            Reaction.save_all(Q)

    @classmethod
    def __update_master_and_id_from_rhea2biocyc(cls, list_reaction_infos):
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

        bulk_size = 750
        start = 0
        stop = start + bulk_size
        while True:
            if start >= len(rhea_ids):
                break
            q = Reaction.select().where(Reaction.rhea_id << rhea_ids[start:stop])
            for reaction in q:
                if reaction.rhea_id in master_ids:
                    reaction.set_master_id(master_ids[reaction.rhea_id])
                if reaction.rhea_id in biocyc_ids:
                    reaction.append_biocyc_id(biocyc_ids[reaction.rhea_id])
            start = stop - 1
            stop = start + bulk_size
            Reaction.save_all(q)

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
        bulk_size = 750
        start = 0
        stop = start + bulk_size
        while True:
            if start >= len(rhea_ids):
                break
            q = Reaction.select().where(Reaction.rhea_id << rhea_ids[start:stop])
            for reaction in q:
                if reaction.rhea_id in master_ids:
                    reaction.set_master_id(master_ids[reaction.rhea_id])
                if reaction.rhea_id in kegg_ids:
                    reaction.set_kegg_id(kegg_ids[reaction.rhea_id])
            start = stop - 1
            stop = start + bulk_size
            Reaction.save_all(q)

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
        bulk_size = 750
        start = 0
        stop = start + bulk_size
        while True:
            if start >= len(rhea_ids):
                break
            q = Reaction.select().where(Reaction.rhea_id << rhea_ids[start:stop])
            for reaction in q:
                reaction.set_direction(direction)
            start = stop - 1
            stop = start + bulk_size
            Reaction.save_all(q)
