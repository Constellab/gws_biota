import os, sys
from hello.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked
from hello.ontology import Ontology
from onto.go_parser import create_ontology_from_file, obo_parser_from_ontology
from peewee import CharField, chunked
from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

####################################################################################
#
# GO class
#
####################################################################################

class GO(Ontology):
    go_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    namespace = CharField(null=True, index=True)
    definition = CharField(null=True, index=True)
    _table_name = 'GO'
    pass

    #setters
    def set_go_id(self, id):
        self.go_id = id

    def set_name(self, name__):
        self.name = name__
    
    def set_namespace(self, namespace__):
        self.namespace = namespace__
    
    def set_definition(self, def__):
        self.definition = def__
    
    #insert functions

    def insert_go_id(list__, key):
        for go in list__:
            go.set_go_id(go.data[key])

    def insert_name(list__, key):
        for go in list__:
            go.set_name(go.data[key])

    def insert_namespace(list__, key):
        for go in list__:
            go.set_namespace(go.data[key])

    def insert_definition(list__, key):
        for go in list__:
            go.set_definition(go.data[key])

    #create go
    def create_go(self, list_go_):
        gos = [GO(data = dict_) for dict_ in list_go_]
        GO.insert_go_id(gos,"id")
        GO.insert_name(gos, "name")
        GO.insert_namespace(gos, "namespace")
        GO.insert_definition(gos, "definition")
        status = 'ok'
        return(status)


    class Meta():
        table_name = 'GO'