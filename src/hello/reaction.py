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
    substrates = CharField(null=True, index=True)
    products = CharField(null=True, index=True)
    enzymes = CharField(null=True, index=True)
    _table_name = 'reaction'

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

    #def set_definition(self, definition__):
        #self.definition = definition__

    def create_reactions(self, list_reaction):
        reactions = [Reaction(data = dict) for dict in list_reaction]
        for react in reactions:
            if('ENTRY' in react.data.keys()):
                react.set_source_accession(react.data['ENTRY'])
            if('DIRECTION' in react.data.keys()):
                react.set_direction(react.data['DIRECTION'])
            if('SUBSTRATES' in react.data.keys()):
                react.set_substrates(react.data['SUBSTRATES'])
            if('PRODUCTS' in react.data.keys()):
                react.set_products(react.data['PRODUCTS'])
            if('ENZYME' in react.data.keys()):
                react.set_enzymes(react.data['ENZYME'])
        status = 'ok'
        return(reactions)

    class Meta:
        table_name = 'reaction'
