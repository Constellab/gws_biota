import os, sys
from gena.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked
from gena.ontology import Ontology
from onto.ontology import Onto
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
    _table_name = 'go'
    pass

    #Setters
    def set_definition(self, def__):
        self.definition = def__

    def set_go_id(self, id):
        self.go_id = id

    def set_name(self, name__):
        self.name = name__
    
    def set_namespace(self, namespace__):
        self.namespace = namespace__
    
    #Inserts
    def insert_definition(list__, key):
        for go in list__:
            go.set_definition(go.data[key])

    def insert_go_id(list__, key):
        for go in list__:
            go.set_go_id(go.data[key])

    def insert_name(list__, key):
        for go in list__:
            go.set_name(go.data[key])

    def insert_namespace(list__, key):
        for go in list__:
            go.set_namespace(go.data[key])

    #create go
    @classmethod
    def create_go(cls, input_db_dir, **files):
        onto_go = Onto.create_ontology_from_file(input_db_dir, files["go_data"])
        list_go = Onto.parse_obo_from_ontology(onto_go)
        gos = [cls(data = dict_) for dict_ in list_go]
        cls.insert_go_id(gos,"id")
        cls.insert_name(gos, "name")
        cls.insert_namespace(gos, "namespace")
        cls.insert_definition(gos, "definition")
        return(list_go)

    class Meta():
        table_name = 'go'