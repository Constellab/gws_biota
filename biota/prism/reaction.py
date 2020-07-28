# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel, DbManager
from gws.prism.controller import Controller

from biota.prism.relation import Relation
from biota.prism.compound import Compound
from biota.prism.enzyme import Enzyme
from biota.prism.go import GO
from biota.helper.rhea import Rhea

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

class Reaction(Relation):
    """
    This class allows to load RHEA reactions entities in the database
    
    enzymes are automatically created by the create_reactions_from_files() method
    
    :type source_accession: CharField
    :property source_accession: rhea identifiers of the reaction
    :type master_id: CharField
    :property master_id: master id of the reaction
    :type direction: CharField
    :property direction: direction of the reaction 
    (UN: undirected, LR: left-right, RL: right-left, BI: bidirectionnal)
    :type biocyc_ids: CharField
    :property biocyc_ids: reaction identifier in the biocyc database
    :type kegg_id: CharField
    :property kegg_id: reaction identifier in the kegg databse
    :type substrates: Compound
    :property substrates: substrates of the reaction
    :type products: Compound
    :property products: products of the reaction
    :type enzymes: Enzyme
    :property enzymes: enzymes of the reaction

    """
    source_accession = CharField(null=True, index=True)
    master_id = CharField(null=True, index=True)
    direction = CharField(null=True, index=True)
    biocyc_ids = CharField(null=True, index=True)
    kegg_id = CharField(null=True, index=True)
    substrates = ManyToManyField(Compound, backref='is_substrate_of', through_model = ReactionSubstrateDeferred)
    products = ManyToManyField(Compound, backref='is_product_of', through_model = ReactionProductDeferred)
    enzymes = ManyToManyField(Enzyme, backref='is_enzyme_of', through_model = ReactionEnzymeDeferred)
    _table_name = 'reactions'

    # -- C --
      
    @classmethod
    def create_reactions_from_files(cls, input_db_dir, **files):
        """
        Creates and registers chebi reaction entities in the database
        Use the rhea helper of biota to get all reactions in a list
        Creates reactions by the calling __create_reactions() method
        Collects directions of reactions and set them by calling the 
        update_direction_from_list() method
        Collects external identifiers of reactions such as ecocy, 
        reactome or kegg identifiers and set them by calling
        _update_master_and_id_(...)() methods
        Register compounds by calling the save_all() method 

        :type input_db_dir: str
        :param input_db_dir: path to the folder that contain the go.obo file
        :type files: dict
        :param files: dictionnary that contains all data files names
        :returns: None
        :rtype: None

        """
        list_react = Rhea.parse_reaction_from_file(input_db_dir, files['rhea_kegg_reaction_file'])
        cls.__create_reactions(list_react)

        list_directions = Rhea.parse_csv_from_file(input_db_dir, files['rhea_direction_file'])
        list_master, list_LR, list_RL, list_BI = Rhea.get_columns_from_lines(list_directions)

        cls._update_direction_from_list(list_master, 'UN')
        cls._update_direction_from_list(list_LR, 'LR')
        cls._update_direction_from_list(list_RL, 'RL')
        cls._update_direction_from_list(list_BI, 'BI')

        list_ecocyc_react = Rhea.parse_csv_from_file(input_db_dir, files['rhea2ecocyc_file'])
        list_metacyc_react = Rhea.parse_csv_from_file(input_db_dir, files['rhea2metacyc_file'])
        list_macie_react = Rhea.parse_csv_from_file(input_db_dir, files['rhea2macie_file'])
        
        cls._update_master_and_id_from_rhea2biocyc(list_ecocyc_react)
        cls._update_master_and_id_from_rhea2biocyc(list_metacyc_react)
        cls._update_master_and_id_from_rhea2biocyc(list_macie_react)
    
        list_kegg_react = Rhea.parse_csv_from_file(input_db_dir, files['rhea2kegg_reaction_file'])
        list_ec_react = Rhea.parse_csv_from_file(input_db_dir, files['rhea2ec_file'])
        list_reactome_react = Rhea.parse_csv_from_file(input_db_dir, files['rhea2reactome_file'])

        cls._update_master_and_id_from_rhea2kegg(list_kegg_react)
        cls._update_master_and_id_from_rhea2ec(list_ec_react)
        cls._update_master_and_id_from_rhea2ec(list_reactome_react)

    @classmethod
    def __create_reactions(cls, list_reaction):
        """

        Creates reactions from a list
        Add reactions-substrates and reaction-products relation in
        reaction_subtrates and reations_products by calling
        set_substrates(), set_products()

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
            react.set_substrates()
            react.set_products()
            if('enzyme' in react.data.keys()):
                react.set_enzymes()
        
        cls.save_all(reactions)

        return reactions

    @classmethod
    def create_table(cls, *args, **kwargs):
        """

        Creates tables related to reaction entities such as reactions, reactions_enzymes,
        reactions_products, etc...
        Uses the super() method of the gws.model object

        """
        super().create_table(*args, **kwargs)
        ReactionSubstrate.create_table()
        ReactionProduct.create_table()
        ReactionEnzyme.create_table()

    # -- D -- 

    @classmethod
    def drop_table(cls, *args, **kwargs):
        """
        
        Drops tables related to GO entities such as reactions, reactions_enzymes,
        reactions_products, etc...
        Uses the super() method of the gws.model object

        """
        ReactionSubstrate.drop_table()
        ReactionProduct.drop_table()
        ReactionEnzyme.drop_table()
        super().drop_table(*args, **kwargs)

    # -- S -- 
    
    def set_biocyc_ids(self, ext_id_):
        try:
            self.biocyc_ids.append(ext_id_)
        except:
            self.biocyc_ids = []
            self.biocyc_ids.append(ext_id_)

    def set_direction(self, direction__):
        self.direction = direction__

    def set_enzymes(self):
        for i in range(0,len(self.data['enzyme'])):
            try:
                enzym = Enzyme.get(Enzyme.ec == str(self.data['enzyme'][i]))
                self.enzymes.add(enzym)
            except:
                pass
                #print("ec not found")
            
    def set_kegg_id(self, kegg_id):
        self.kegg_id = kegg_id
    
    def set_master_id(self, master_id_):
        self.master_id = master_id_
    
    def set_products(self):
        for i in range(0,len(self.data['products'])):
            comp = Compound.get(Compound.source_accession == str(self.data['products'][i]))
            self.products.add(comp)

    def set_source_accession(self, source__):
        self.source_accession = source__

    def set_substrates(self):
        for i in range(0,len(self.data['substrates'])):
            comp = Compound.get(Compound.source_accession == str(self.data['substrates'][i]))
            self.substrates.add(comp)

    # -- U --

    @classmethod
    def _update_master_and_id_from_rhea2ec(cls, list_reaction_infos):
        """

        Get informations about master id and biocyc id of from a rhea2ec.tsv file
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
                    rea.set_biocyc_ids(biocyc_ids[rea.source_accession])

            start = stop - 1
            stop = start + bulk_size

            cls.save_all(q)

    @classmethod
    def _update_master_and_id_from_rhea2biocyc(cls, list_reaction_infos):
        """
        
        Get informations about master id and biocyc id of from a rhea2biocyc.tsv file
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
                    rea.set_biocyc_ids(biocyc_ids[rea.source_accession])

            start = stop - 1
            stop = start + bulk_size

            cls.save_all(q)

        # for dict__ in list_reaction_infos:
        #     try:
        #       rea = cls.get(cls.source_accession == 'RHEA:' + dict__['rhea_id'])  
        #       rea.set_master_id(dict__['master_id'])
        #       rea.set_biocyc_ids(dict__['id'])
        #     except:
        #         print('can not find the reaction RHEA:' + dict__['rhea_id'])

    @classmethod
    def _update_master_and_id_from_rhea2kegg(cls, list_reaction_infos):
        """
        
        Get informations about master id and biocyc id of from a rhea2kegg.tsv file
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

        # for dict__ in list_reaction_infos:
        #     try:
        #       rea = cls.get(cls.source_accession == 'RHEA:' + dict__['rhea_id'])  
        #       rea.set_master_id(dict__['master_id'])
        #       rea.set_kegg_id(dict__['id'])
        #     except:
        #         print('can not find the reaction RHEA:' + dict__['rhea_id'])

    """
    @classmethod
    def _update_master_and_id_from_rhea2ec(cls, list_reaction_infos):
        accessions = []
        master_ids = {}
        for dict__ in list_reaction_infos:
            accession = 'RHEA:'+dict__['rhea_id']
            accessions.append(accession)
            master_ids[accession] = dict__['master_id']

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

            start = stop - 1
            stop = start + bulk_size

            cls.save_all(q)
    """

    @classmethod
    def _update_direction_from_list(cls, list_direction, direction):
        """
        
        Get informations about direction of from rhea.tsv files and
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
    
    This class refers to substrates of rhea reactions

    ReactionSubstrate entities are created by the __create_reactions() method 
    which get substrates of reactions directly from their data

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
    
    This class refers to products of rhea reactions

    ReactionProduct entities are created by the __create_reactions() method 
    which get products of reactions directly from their data

    :type compound: Compound 
    :property compound: product of the reaction
    :type reaction: Reaction 
    :property reaction: concerned reaction
    
    """
    compound = ForeignKeyField(Compound)
    reaction = ForeignKeyField(Reaction)
    class Meta:
        table_name = 'reactions_products'
        database = DbManager.db

class ReactionEnzyme(PWModel):
    """
    
    This class refers to products of rhea reactions

    ReactionProduct entities are created by the __create_reactions() method 
    which get enzymes of reactions directly from their data

    :type enzyme: Enzyme 
    :property enzyme: enzyme of the reaction
    :type reaction: Reaction 
    :property reaction: concerned reaction
    
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