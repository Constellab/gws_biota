from gws.settings import Settings
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Resource, ResourceViewModel
from gws.prism.controller import Controller
from gena.relation import Relation
from peewee import CharField, Model, chunked
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
    external_database_id = CharField(null=True, index=True)
    direction = CharField(null=True, index=True)
    substrates = CharField(null=True, index=True)
    products = CharField(null=True, index=True)
    enzymes = CharField(null=True, index=True)
    master_id = CharField(null=True, index=True)
    biocyc_id = CharField(null=True, index=True)
    kegg_id = CharField(null=True, index=True)
    #json = JSONField(null = True, default={})
    _table_name = 'reactions'

    #setter function
    def set_source_accession(self, source__):
        self.source_accession = source__

    def set_direction(self, direction__):
        self.direction = direction__

    def set_substrates(self, substrates__):
        self.substrates = substrates__
    
    def set_products(self, products__):
        self.products = products__
    
    def set_enzymes(self, enzymes__):
        self.enzymes = enzymes__
    
    def set_master_id(self, master_id_):
        self.master_id = master_id_

    def set_biocyc_id(self, ext_id_):
        self.biocyc_id = ext_id_
    
    def set_kegg_id(self, _kegg_id_):
        self._kegg_id = _kegg_id_
    
    def set_json(self, json_):
        self.json = json_

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

    def get_direction(list_reaction_direction):
        list_test = []
        for dict_ in list_reaction_direction:
            if('rhea_id' in dict_.keys()):
                try:
                    rea = Reaction.get(Reaction.source_accession == 'RHEA:' + dict_['rhea_id'])
                    if(rea.direction == None): #not sure if necessary
                        #print('ok')
                        rea.set_direction(dict_['direction'])
                        rea.set_master_id(dict_['master_id'])
                        rea.set_biocyc_id(dict_['id'])
                except:
                    print('can not find the reaction RHEA:' + str(dict_['rhea_id']))
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
