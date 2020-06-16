from gws.settings import Settings
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Resource, ResourceViewModel
from gws.prism.controller import Controller
from gena.relation import Relation
from gena.compound import Compound
from rhea.rhea import Rhea
from peewee import CharField, ForeignKeyField, Model, chunked, ManyToManyField, DeferredThroughModel
from peewee import Model as PWModel
from manage import settings
from gws.prism.controller import Controller
from gws.prism.model import DbManager
from playhouse.sqlite_ext import JSONField

####################################################################################
#
# Reaction class
#
####################################################################################

path = settings.get_data("gena_db_path")

ReactionSubstrateDeferred = DeferredThroughModel()
ReactionProductDeferred = DeferredThroughModel()

class Reaction(Relation):
    source_accession = CharField(null=True, index=True)
    master_id = CharField(null=True, index=True)
    direction = CharField(null=True, index=True)
    enzymes = CharField(null=True, index=True)
    master_id = CharField(null=True, index=True)
    biocyc_id = CharField(null=True, index=True)
    kegg_id = CharField(null=True, index=True)
    substrates = ManyToManyField(Compound, backref='is_substrate_of', through_model = ReactionSubstrateDeferred)
    products = ManyToManyField(Compound, backref='is_product_of', through_model = ReactionProductDeferred)

    _table_name = 'reactions'

    #setter function
    def set_source_accession(self, source__):
        self.source_accession = source__

    def set_direction(self, direction__):
        self.direction = direction__

    def set_substrates(self):
        for i in range(0,len(self.data['substrates'])):
            comps = Compound.get(Compound.source_accession == str(self.data['substrates'][i]))
            self.substrates.add(comps)
    
    def set_products(self):
        for i in range(0,len(self.data['products'])):
            comps = Compound.get(Compound.source_accession == str(self.data['products'][i]))
            self.products.add(comps)
    
    def set_enzymes(self, enzymes__):
        self.enzymes = enzymes__
    
    def set_master_id(self, master_id_):
        self.master_id = master_id_

    def set_biocyc_id(self, ext_id_):
        self.biocyc_id = ext_id_
    
    def set_kegg_id(self, kegg_id):
        self.kegg_id = kegg_id

    @classmethod
    def create_reactions_from_files(cls, input_db_dir, **files):
        list_react = Rhea.parse_reaction_from_file(input_db_dir, files['rhea_kegg_reaction_file'])
        cls.__create_reactions(list_react)
        Controller.save_all()

        list_directions = Rhea.parse_csv_from_file(input_db_dir, files['rhea_direction_file'])
        list_master, list_LR, list_RL, list_BI = Rhea.get_columns_from_lines(list_directions)
        cls.__set_direction_from_list(list_master, 'UN')
        cls.__set_direction_from_list(list_LR, 'LR')
        cls.__set_direction_from_list(list_RL, 'RL')
        cls.__set_direction_from_list(list_BI, 'BI')
        Controller.save_all()

        list_ecocyc_react = Rhea.parse_csv_from_file(input_db_dir, files['rhea2ecocyc_file'])
        list_metacyc_react = Rhea.parse_csv_from_file(input_db_dir, files['rhea2metacyc_file'])
        list_macie_react = Rhea.parse_csv_from_file(input_db_dir, files['rhea2macie_file'])

        cls.__get_master_and_id(list_ecocyc_react)
        cls.__get_master_and_id(list_metacyc_react)
        cls.__get_master_and_id(list_macie_react)
        
        list_kegg_react = Rhea.parse_csv_from_file(input_db_dir, files['rhea2kegg_reaction_file'])
        list_ec_react = Rhea.parse_csv_from_file(input_db_dir, files['rhea2ec_file'])

        cls.__get_master_and_id_from_rhea2kegg(list_kegg_react)
        cls.__get_master_and_id_from_rhea2ec(list_ec_react)

        Controller.save_all()

    @classmethod
    def __create_reactions(cls, list_reaction):
        reactions = [cls(data = dict) for dict in list_reaction]
        for react in reactions:
            if('entry' in react.data.keys()):
                react.set_source_accession(react.data['entry'])
            if('enzyme' in react.data.keys()):
                react.set_enzymes(react.data['enzyme'])
            react.save()
            react.set_substrates()
            react.set_products()
        status = 'ok'
        return(reactions)

    @classmethod
    def __set_direction_from_list(cls, list_direction, direction):
        for i in range(0, len(list_direction)):
            try:
                rea = cls.get(cls.source_accession == 'RHEA:' + list_direction[i])
                if(rea.direction == None):
                    rea.set_direction(direction)
            except:
                print('can not find the reaction RHEA:' + list_direction[i])
        status = 'ok'
        return(status)
    
    @classmethod
    def __get_master_and_id(cls, list_reaction_infos):
        for dict__ in list_reaction_infos:
            try:
              rea = cls.get(cls.source_accession == 'RHEA:' + dict__['rhea_id'])  
              rea.set_master_id(dict__['master_id'])
              rea.set_biocyc_id(dict__['id'])
            except:
                print('can not find the reaction RHEA:' + dict__['rhea_id'])
        status = 'ok'
        return(status)

    @classmethod
    def __get_master_and_id_from_rhea2kegg(cls, list_reaction_infos):
        for dict__ in list_reaction_infos:
            try:
              rea = cls.get(cls.source_accession == 'RHEA:' + dict__['rhea_id'])  
              rea.set_master_id(dict__['master_id'])
              rea.set_kegg_id(dict__['id'])
            except:
                print('can not find the reaction RHEA:' + dict__['rhea_id'])
        status = 'ok'
        return(status)

    @classmethod
    def __get_master_and_id_from_rhea2ec(cls, list_reaction_infos):
        for dict__ in list_reaction_infos:
            try:
              rea = cls.get(cls.source_accession == 'RHEA:' + dict__['rhea_id'])  
              rea.set_master_id(dict__['master_id'])
            except:
                print('can not find the reaction RHEA:' + dict__['rhea_id'])
        status = 'ok'
        return(status)

    class Meta:
        table_name = 'reactions'


class ReactionSubstrate(PWModel):
    compound = ForeignKeyField(Compound)
    reaction = ForeignKeyField(Reaction)
    class Meta:
        table_name = 'reactions_subsrates'
        database = DbManager.db


class ReactionProduct(PWModel):
    compound = ForeignKeyField(Compound)
    reaction = ForeignKeyField(Reaction)
    class Meta:
        table_name = 'reactions_products'
        database = DbManager.db
    

ReactionSubstrateDeferred.set_model(ReactionSubstrate)
ReactionProductDeferred.set_model(ReactionProduct)