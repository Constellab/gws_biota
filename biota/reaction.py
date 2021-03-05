# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField, ManyToManyField, DeferredThroughModel
from peewee import Model as PWModel

from biota.base import Base, DbManager
from biota.entity import Entity
from biota.compound import Compound
from biota.enzyme import Enzyme

####################################################################################
#
# Reaction class
#
####################################################################################

ReactionSubstrateDeferred = DeferredThroughModel()
ReactionProductDeferred = DeferredThroughModel()
ReactionEnzymeDeferred = DeferredThroughModel()

class Reaction(Entity):
    """
    This class represents metabolic reactions extracted from Rhea database.

    Rhea is an expert curated resource of biochemical reactions designed for the 
    annotation of enzymes and genome-scale metabolic networks and models (https://www.rhea-db.org/).
    Rhea data are available under the Creative 
    Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

    :property rhea_id: rhea accession number
    :type rhea_id: CharField
    :property master_id: master id of the reaction
    :type master_id: CharField
    :property direction: direction of the reaction 
    :type direction: CharField (UN = undirected, LR = left-right, RL = right-left, BI = bidirectionnal)
    :property biocyc_ids: reaction identifier in the biocyc database
    :type biocyc_ids: CharField
    :property kegg_id: reaction identifier in the kegg databse
    :type kegg_id: CharField
    :property substrates: substrates of the reaction
    :type substrates: List of `Compound`
    :property products: products of the reaction
    :type products: List of `Compound`
    :property enzymes: enzymes of the reaction
    :type enzymes: List of `Enzyme`
    """
    rhea_id = CharField(null=True, index=True)
    master_id = CharField(null=True, index=True)
    direction = CharField(null=True, index=True)
    
    biocyc_ids = CharField(null=True, index=True)
    #brenda_id = CharField(null=True, index=True)
    metacyc_id = CharField(null=True, index=True)
    kegg_id = CharField(null=True, index=True)
    sabio_rk_id = CharField(null=True, index=True)

    substrates = ManyToManyField(Compound, through_model = ReactionSubstrateDeferred)
    products = ManyToManyField(Compound, through_model = ReactionProductDeferred)
    enzymes = ManyToManyField(Enzyme, through_model = ReactionEnzymeDeferred)

    _fts_fields = { **Entity._fts_fields, 'definition': 2.0 }
    _table_name = 'biota_reaction'

    # -- A --

    def append_biocyc_id(self, id):
        """
        Appends a biocyc id to the reaction

        :param id: The id
        :type id: str
        """
        try:
            self.biocyc_ids.append(id)
        except:
            self.biocyc_ids = []
            self.biocyc_ids.append(id)

    # -- C --
      
    @classmethod
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

        from biota._helper.rhea import Rhea

        job = kwargs.get('job',None)
        list_of_reactions = Rhea.parse_reaction_from_file(biodata_dir, kwargs['rhea_reaction_file'])
        cls.__create_reactions(list_of_reactions, job=job)

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
    def __create_reactions(cls, list_reaction, job=None):
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
        reactions = [cls(data = dict) for dict in list_reaction]
        for react in reactions:
            if 'entry' in react.data.keys():
                react.rhea_id = react.data['entry']
                del react.data['entry']

            if not job is None:
                react._set_job(job)

        cls.save_all(reactions)

        for react in reactions:
            react.__set_substrates_from_data()
            react.__set_products_from_data()
            if 'enzymes' in react.data.keys():
                react.__set_enzymes_from_data()
        
        cls.save_all(reactions)

        return reactions

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `reaction` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        ReactionSubstrate.create_table()
        ReactionProduct.create_table()
        ReactionEnzyme.create_table()

    # -- D -- 

    @property
    def definition(self):
        return self.data["definition"]

    @classmethod
    def drop_table(cls, *args, **kwargs):
        """
        Drops `reaction` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        ReactionSubstrate.drop_table()
        ReactionProduct.drop_table()
        ReactionEnzyme.drop_table()
        super().drop_table(*args, **kwargs)

    # -- G --

    def get_title(self, default=None):
        return self.definition

    # -- I -- 

    def is_charge_balanced(self):
        total_substrate_charge = 0
        total_product_charge = 0

        for s in self.substrates:
            total_substrate_charge = total_substrate_charge + s.charge
        
        for p in self.products:
            total_product_charge = total_product_charge + p.charge

        return total_substrate_charge == total_product_charge

    def is_mass_balanced(self):
        total_substrate_mass = 0
        total_product_mass = 0

        for s in self.substrates:
            total_substrate_mass = total_substrate_mass + s.mass
        
        for p in self.products:
            total_product_mass = total_product_mass + p.mass

        return total_substrate_mass == total_product_mass

    # -- S -- 

    def set_direction(self, direction):
        """
        Set the direction of the reaction

        :param direction: The direction
        :type direction: str
        """
        self.direction = direction
            
    def set_kegg_id(self, kegg_id):
        """
        Set the KEGG id the reaction

        :param kegg_id: The kegg id
        :type kegg_id: str
        """
        self.kegg_id = kegg_id
    
    def set_rhea_id(self, kegg_id):
        """
        Set the RHEA id the reaction

        :param rhea_id: The RHEA id
        :type rhea_id: str
        """
        self.kegg_id = kegg_id

    def set_master_id(self, master_id):
        """
        Set the master id the reaction

        :param master_id: The master id
        :type master_id: str
        """
        self.master_id = master_id

    def __set_substrates_from_data(self):
        """
        Set substrates from `data`
        """
        Q = Compound.select().where(Compound.chebi_id << self.data['substrates'])
        for comp in Q:
            self.substrates.add(comp)
    
    def __set_products_from_data(self):
        """
        Set products from `data`
        """
        Q = Compound.select().where(Compound.chebi_id << self.data['products'])
        for comp in Q:
            self.products.add(comp)
    
    def __set_enzymes_from_data(self):
        """
        Set enzymes from `data`
        """
        from biota.enzyme import Enzyme
        Q = Enzyme.select().where(Enzyme.ec_number << self.data['enzymes'])
        for enz in Q:
            self.enzymes.add(enz)

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

            Q = cls.select().where(cls.rhea_id << rhea_ids[start:stop])

            for reaction in Q:
                if reaction.rhea_id in biocyc_ids:
                    reaction.append_biocyc_id(biocyc_ids[reaction.rhea_id])

            start = stop
            stop = start + bulk_size

            cls.save_all(Q)

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

            q = cls.select().where(cls.rhea_id << rhea_ids[start:stop])
   
            for reaction in q:
                if reaction.rhea_id in master_ids:
                    reaction.set_master_id(master_ids[reaction.rhea_id])
                
                if reaction.rhea_id in biocyc_ids:
                    reaction.append_biocyc_id(biocyc_ids[reaction.rhea_id])

            start = stop - 1
            stop = start + bulk_size

            cls.save_all(q)

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

            q = cls.select().where(cls.rhea_id << rhea_ids[start:stop])

            for reaction in q:
                if reaction.rhea_id in master_ids:
                    reaction.set_master_id(master_ids[reaction.rhea_id])
                
                if reaction.rhea_id in kegg_ids:
                    reaction.set_kegg_id(kegg_ids[reaction.rhea_id])

            start = stop - 1
            stop = start + bulk_size

            cls.save_all(q)

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

            q = cls.select().where(cls.rhea_id << rhea_ids[start:stop])

            for reaction in q:
                reaction.set_direction(direction)

            start = stop - 1
            stop = start + bulk_size

            cls.save_all(q)



class ReactionSubstrate(PWModel):
    """
    This class defines the many-to-many relationship between susbtrates and reactions.

    :type compound: Compound 
    :property compound: subtrate of the reaction
    :type reaction: Reaction 
    :property reaction: concerned reaction
    """
    compound = ForeignKeyField(Compound)
    reaction = ForeignKeyField(Reaction)
    
    class Meta:
        table_name = 'biota_reaction_substrates'
        database = DbManager.db


class ReactionProduct(PWModel):
    """
    This class defines the many-to-many relationship between products and reactions.

    :property compound: product of the reaction
    :type compound: Compound 
    :property reaction: concerned reaction 
    :type reaction: Reaction 
    """
    compound = ForeignKeyField(Compound)
    reaction = ForeignKeyField(Reaction)
    
    class Meta:
        table_name = 'biota_reaction_products'
        database = DbManager.db

class ReactionEnzyme(PWModel):
    """
    This class defines the many-to-many relationship between enzymes and reactions.

    :property enzyme: enzyme of the reaction
    :type enzyme: Enzyme 
    
    :property reaction: concerned reaction
    :type reaction: Reaction 
    """
    enzyme = ForeignKeyField(Enzyme)
    reaction = ForeignKeyField(Reaction)
    
    class Meta:
        table_name = 'biota_reaction_enzymes'
        database = DbManager.db

ReactionSubstrateDeferred.set_model(ReactionSubstrate)
ReactionProductDeferred.set_model(ReactionProduct)
ReactionEnzymeDeferred.set_model(ReactionEnzyme)