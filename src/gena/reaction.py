from gws.settings import Settings
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Resource, ResourceViewModel
from gws.prism.controller import Controller
from gena.relation import Relation
from peewee import CharField, Model, chunked, ManyToManyField
from manage import settings
from playhouse.sqlite_ext import JSONField

####################################################################################
#
# Reaction class
#
####################################################################################

path = settings.get_data("gena_db_path")

class Reaction(Relation):
    source_accession = CharField(null=True, index=True)
    master_id = CharField(null=True, index=True)
    direction = CharField(null=True, index=True)
    #substrates = CharField(null=True, index=True)
    #products = CharField(null=True, index=True)
    enzymes = CharField(null=True, index=True)
    master_id = CharField(null=True, index=True)
    biocyc_id = CharField(null=True, index=True)
    kegg_id = CharField(null=True, index=True)

    #substrates = ManyToManyField(Compound, backref='is_substrate_of')
    #products = ManyToManyField(Compound, backref='is_product_of')

    _table_name = 'reactions'

    #setter function
    def set_source_accession(self, source__):
        self.source_accession = source__

    def set_direction(self, direction__):
        self.direction = direction__

    def set_substrates(self, substrates__):
        #comps = Compound.select(Compound.id == )
        self.substrates = substrates__ 
    
    def set_products(self, products__):
        self.products = products__
    
    def set_enzymes(self, enzymes__):
        self.enzymes = enzymes__
    
    def set_master_id(self, master_id_):
        self.master_id = master_id_

    def set_biocyc_id(self, ext_id_):
        self.biocyc_id = ext_id_
    
    def set_kegg_id(self, kegg_id):
        self.kegg_id = kegg_id


    @classmethod
    def create_reactions(cls, list_reaction):
        reactions = [cls(data = dict) for dict in list_reaction]
        for react in reactions:
            if('entry' in react.data.keys()):
                react.set_source_accession(react.data['entry'])
            if('substrates' in react.data.keys()):
                react.set_substrates(react.data['substrates'])
            if('products' in react.data.keys()):
                react.set_products(react.data['products'])
            if('enzyme' in react.data.keys()):
                react.set_enzymes(react.data['enzyme'])
        status = 'ok'
        return(reactions)

    @classmethod
    def set_direction_from_list(cls, list_direction, direction):
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
    def get_master_and_id(cls, list_reaction_infos):
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
    def get_master_and_id_from_rhea2kegg(cls, list_reaction_infos):
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
    def get_master_and_id_from_rhea2ec(cls, list_reaction_infos):
        for dict__ in list_reaction_infos:
            try:
              rea = cls.get(cls.source_accession == 'RHEA:' + dict__['rhea_id'])  
              rea.set_master_id(dict__['master_id'])
            except:
                print('can not find the reaction RHEA:' + dict__['rhea_id'])
        status = 'ok'
        return(status)



    """
    def test_json(self, list_react):
        dict_reactions_test = {}
        dict_reactions_test['CHEBI:133894'] =  1
        dict_reactions_test['CHEBI:15378'] =  5
        dict_reactions_test['CHEBI:58223'] =  5
        for reactions in list_react:
            print(type(reactions.json))
            #reactions.json.set(dict_reactions_test, as_json = True)
            print(reactions.json)
        #self.json.set(dict_reactions_test, as_json = True)
        return(dict_reactions_test)
    """
    class Meta:
        table_name = 'reactions'
