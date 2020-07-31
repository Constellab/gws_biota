# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com


from gws.prism.model import Resource, ResourceViewModel, DbManager
from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate

from biota.db.entity import Entity
from biota.db.compound import Compound
from biota.db.enzyme import Enzyme
from biota.db.go import GO
from biota._helper.rhea import Rhea

from peewee import CharField, ForeignKeyField, ManyToManyField, DeferredThroughModel
from peewee import Model as PWModel

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

    :property source_accession: rhea identifiers of the reaction
    :type source_accession: CharField
    :property master_id: master id of the reaction
    :type master_id: CharField
    :property direction: direction of the reaction 
    :type direction: CharField
        (UN: undirected, LR: left-right, RL: right-left, BI: bidirectionnal)
    :property biocyc_ids: reaction identifier in the biocyc database
    :type biocyc_ids: CharField
    :property kegg_id: reaction identifier in the kegg databse
    :type kegg_id: CharField
    :property substrates: substrates of the reaction
    :type substrates: Compound
    :property products: products of the reaction
    :type products: Compound
    :property enzymes: enzymes of the reaction
    :type enzymes: Enzyme
    """

    source_accession = CharField(null=True, index=True)
    master_id = CharField(null=True, index=True)
    direction = CharField(null=True, index=True)
    biocyc_ids = CharField(null=True, index=True)
    kegg_id = CharField(null=True, index=True)
    substrates = ManyToManyField(Compound, backref='is_substrate_of', through_model = ReactionSubstrateDeferred)
    products = ManyToManyField(Compound, backref='is_product_of', through_model = ReactionProductDeferred)
    enzymes = ManyToManyField(Enzyme, backref='is_enzyme_of', through_model = ReactionEnzymeDeferred)
    _table_name = 'reaction'

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
    def create_reaction_db(cls, biodata_db_dir, **files):
        """
        Creates and fills the `reaction` database

        :param biodata_db_dir: path to the folder that contain the go.obo file
        :type biodata_db_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """
        list_react = Rhea.parse_reaction_from_file(biodata_db_dir, files['rhea_kegg_reaction_file'])
        cls.__create_reactions(list_react)

        list_directions = Rhea.parse_csv_from_file(biodata_db_dir, files['rhea_direction_file'])
        list_master, list_LR, list_RL, list_BI = Rhea.get_columns_from_lines(list_directions)

        cls.__update_direction_from_list(list_master, 'UN')
        cls.__update_direction_from_list(list_LR, 'LR')
        cls.__update_direction_from_list(list_RL, 'RL')
        cls.__update_direction_from_list(list_BI, 'BI')

        list_ecocyc_react = Rhea.parse_csv_from_file(biodata_db_dir, files['rhea2ecocyc_file'])
        list_metacyc_react = Rhea.parse_csv_from_file(biodata_db_dir, files['rhea2metacyc_file'])
        list_macie_react = Rhea.parse_csv_from_file(biodata_db_dir, files['rhea2macie_file'])
        
        cls.__update_master_and_id_from_rhea2biocyc(list_ecocyc_react)
        cls.__update_master_and_id_from_rhea2biocyc(list_metacyc_react)
        cls.__update_master_and_id_from_rhea2biocyc(list_macie_react)
    
        list_kegg_react = Rhea.parse_csv_from_file(biodata_db_dir, files['rhea2kegg_reaction_file'])
        list_ec_react = Rhea.parse_csv_from_file(biodata_db_dir, files['rhea2ec_file'])
        list_reactome_react = Rhea.parse_csv_from_file(biodata_db_dir, files['rhea2reactome_file'])

        cls.__update_master_and_id_from_rhea2kegg(list_kegg_react)
        cls.__update_master_and_id_from_rhea2ec(list_ec_react)
        cls.__update_master_and_id_from_rhea2ec(list_reactome_react)

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
        reactions = [cls(data = dict) for dict in list_reaction]
        for react in reactions:
            if 'entry' in react.data.keys():
                react.set_source_accession(react.data['entry'])
        
        cls.save_all(reactions)

        for react in reactions:
            react.__set_substrates_from_data()
            react.__set_products_from_data()
            if('enzyme' in react.data.keys()):
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
    
    def set_master_id(self, master_id):
        """
        Set the master id the reaction

        :param master_id: The master id
        :type master_id: str
        """
        self.master_id = master_id
    
    def set_source_accession(self, source):
        """
        Set the source accession the reaction

        :param source: The source accession
        :type source: str
        """
        self.source_accession = source

    def __set_substrates_from_data(self):
        """
        Set substrates from `data`
        """
        for i in range(0,len(self.data['substrates'])):
            print(self.data['substrates'])
            comp = Compound.get(Compound.source_accession == str(self.data['substrates'][i]))
            self.substrates.add(comp)
    
    def __set_products_from_data(self):
        """
        Set products from `data`
        """
        for i in range(0,len(self.data['products'])):
            comp = Compound.get(Compound.source_accession == str(self.data['products'][i]))
            self.products.add(comp)

    def __set_enzymes_from_data(self):
        """
        Set enzymes from `data`
        """
        for i in range(0,len(self.data['enzyme'])):
            try:
                enzym = Enzyme.get(Enzyme.ec == str(self.data['enzyme'][i]))
                self.enzymes.add(enzym)
            except:
                pass
                #print("ec not found")
    # -- U --

    @classmethod
    def __update_master_and_id_from_rhea2ec(cls, list_reaction_infos):
        """
        Get informations about master id and biocyc id of from a :file:`rhea2ec.tsv` file
        update those index if the concerned reaction is in the table

        :type list_reaction_infos: list
        :param list_reaction_infos: list of dictionnaries that contains informations about reactions
        """
        accessions = []
        master_ids = {}
        biocyc_ids = {}
        for dict__ in list_reaction_infos:
            accession = 'RHEA:'+dict__['rhea_id']
            accessions.append(accession)
            master_ids[accession] = dict__['master_id']
            biocyc_ids[accession] = dict__['id']

        bulk_size = 750
        start = 0
        stop = start + bulk_size

        while True:
            if start >= len(accessions):
                break

            q = cls.select().where(cls.source_accession << accessions[start:stop])

            for rea in q:
                if rea.source_accession in biocyc_ids:
                    rea.append_biocyc_id(biocyc_ids[rea.source_accession])

            start = stop - 1
            stop = start + bulk_size

            cls.save_all(q)

    @classmethod
    def __update_master_and_id_from_rhea2biocyc(cls, list_reaction_infos):
        """
        Get informations about master id and biocyc id of from a :file:`rhea2biocyc.tsv` file
        update those index if the concerned reaction is in the table

        :type list_reaction_infos: list
        :param list_reaction_infos: list of dictionnaries that contains informations about reactions
        """
        accessions = []
        master_ids = {}
        biocyc_ids = {}
        for dict__ in list_reaction_infos:
            accession = 'RHEA:'+dict__['rhea_id']
            accessions.append(accession)
            master_ids[accession] = dict__['master_id']
            biocyc_ids[accession] = dict__['id']

        bulk_size = 750
        start = 0
        stop = start + bulk_size

        while True:
            if start >= len(accessions):
                break

            q = cls.select().where(cls.source_accession << accessions[start:stop])
   
            for rea in q:
                if rea.source_accession in master_ids:
                    rea.set_master_id(master_ids[rea.source_accession])
                
                if rea.source_accession in biocyc_ids:
                    rea.append_biocyc_id(biocyc_ids[rea.source_accession])

            start = stop - 1
            stop = start + bulk_size

            cls.save_all(q)

        # for dict__ in list_reaction_infos:
        #     try:
        #       rea = cls.get(cls.source_accession == 'RHEA:' + dict__['rhea_id'])  
        #       rea.set_master_id(dict__['master_id'])
        #       rea.append_biocyc_id(dict__['id'])
        #     except:
        #         print('can not find the reaction RHEA:' + dict__['rhea_id'])

    @classmethod
    def __update_master_and_id_from_rhea2kegg(cls, list_reaction_infos):
        """
        Get informations about master id and biocyc id of from a :file:`rhea2kegg.tsv` file
        update those index if the concerned reaction is in the table

        :type list_reaction_infos: list
        :param list_reaction_infos: list of dictionnaries that contains informations about reactions
        """
        accessions = []
        master_ids = {}
        kegg_ids = {}
        for dict__ in list_reaction_infos:
            accession = 'RHEA:'+dict__['rhea_id']
            accessions.append(accession)
            master_ids[accession] = dict__['master_id']
            kegg_ids[accession] = dict__['id']

        bulk_size = 750
        start = 0
        stop = start + bulk_size

        while True:
            if start >= len(accessions):
                break

            q = cls.select().where(cls.source_accession << accessions[start:stop])

            for rea in q:
                if rea.source_accession in master_ids:
                    rea.set_master_id(master_ids[rea.source_accession])
                
                if rea.source_accession in kegg_ids:
                    rea.set_kegg_id(kegg_ids[rea.source_accession])

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
        accessions = []
        for s in list_direction:
            accessions.append('RHEA:'+s)

        bulk_size = 750
        start = 0
        stop = start + bulk_size
        while True:
            if start >= len(accessions):
                break

            q = cls.select().where(cls.source_accession << accessions[start:stop])

            for rea in q:
                rea.set_direction(direction)

            start = stop - 1
            stop = start + bulk_size

            cls.save_all(q)

    class Meta:
        table_name = 'reaction'


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
        table_name = 'reactions_subsrates'
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
        table_name = 'reactions_products'
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
        table_name = 'reactions_enzymes'
        database = DbManager.db

class ReactionJSONStandardViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.source_accession}},
            "definition": {{view_model.model.data['definition']}},
            }
        """)

class ReactionJSONPremiumViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.source_accession}},
            "definition": {{view_model.model.data['definition']}},
            "equation": {{view_model.model.data['source_equation']}},
            "master_id": {{view_model.model.master_id}},
            "direction" : {{view_model.model.direction}},
            "enzymes": {{view_model.display_enzymes()}},
            "substrates": {{view_model.display_substrates()}},
            "products": {{view_model.display_products()}}
            }
        """)

    def display_enzymes(self):
        q = self.model.enzymes
        list_enzymes = []
        for i in range(0, len(q)):
            list_enzymes.append(q[i].ec)
        if (len(list_enzymes) == 0):
            list_enzymes = None
        return(list_enzymes)
    
    def display_substrates(self):
        q = self.model.substrates
        list_substrates = []
        for i in range(0, len(q)):
            list_substrates.append(q[i].source_accession)
        return(list_substrates)
    
    def display_products(self):
        q = self.model.products
        list_products = []
        for i in range(0, len(q)):
            list_products.append(q[i].source_accession)
        return(list_products)
        

ReactionSubstrateDeferred.set_model(ReactionSubstrate)
ReactionProductDeferred.set_model(ReactionProduct)
ReactionEnzymeDeferred.set_model(ReactionEnzyme)

Controller.register_model_classes([Reaction])