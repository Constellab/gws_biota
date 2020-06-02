from gws.settings import Settings
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Resource, ResourceViewModel
from gws.prism.controller import Controller
from hello.relation import Relation
from peewee import CharField, Model, chunked

####################################################################################
#
# Reaction class
#
####################################################################################


class Reaction(Relation):
    source_accession = CharField(null=True, index=True)
    direction = CharField(null=True, index=True)
    reagents = CharField(null=True, index=True)
    products = CharField(null=True, index=True)
    enzymes = CharField(null=True, index=True)
    definition = CharField(null=True, index=True)
    _table_name = 'reaction'

    #setter function
    def set_source_accession(self, source__):
        self.source_accession = source__

    def set_direction(self, direction__):
        self.direction = direction__

    def set_reagents(self, reagents__):
        self.reagents = reagents__
    
    def set_products(self, products__):
        self.products = products__
    
    def set_enzymes(self, enzymes__):
        self.enzymes = enzymes__

    def set_definition(self, definition__):
        self.definition = definition__

    #insert function
    def insert_source_accession(list__, key):
        for react in list__:
            react.set_source_accession(react.data[key])

    def insert_direction(list__):
        for react in list__:
             react.set_direction(react.data['DIRECTION'])

    def insert_reagents(list__, key):
        for react in list__:
            react.set_reagents(react.data[key])
    
    def insert_products(list__, key):
        for react in list__:
            react.set_products(react.data[key])

    def insert_enzymes(list__, key):
        for react in list__:
            react.set_enzymes(react.data[key])
    
    def insert_definition(list__, key):
        for react in list__:
            react.set_definition(react.data[key])

    def create_reactions(self, list_reaction):
        reactions = [Reaction(data = dict) for dict in list_reaction]
        #Reaction.insert_source_accession(reactions, "ENTRY")
        #Reaction.insert_direction(reactions)
        #Reaction.insert_reagents(reactions, 'REAGENTS')
        #Reaction.insert_products(reactions, 'PRODUCTS')
        #Reaction.insert_enzymes(reactions, 'ENZYME')
        #Reaction.insert_definition(reactions, 'DEFINITION')
        status = 'ok'
        return(status)

    def get_coumpound(self):
        pass

class Meta:
    table_name = 'reaction'
