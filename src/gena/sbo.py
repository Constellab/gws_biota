import os, sys
from gena.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked
from onto.ontology import Onto
from gena.ontology import Ontology
from peewee import CharField, chunked

####################################################################################
#
# SBO class
#
####################################################################################

class SBO(Ontology):
    sbo_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    definition = CharField(null=True, index=True)
    _table_name = 'sbo'
    
    #Setters
    def set_definition(self, def__):
        self.definition = def__

    def set_name(self, name__):
        self.name = name__    

    def set_sbo_id(self, id):
        self.sbo_id = id
    
    #Inserts
    def insert_definition(list__, key):
        for sbo in list__:
            sbo.set_definition(sbo.data[key])
    
    def insert_name(list__, key):
        for sbo in list__:
            sbo.set_name(sbo.data[key])

    def insert_sbo_id(list__, key):
        for sbo in list__:
            sbo.set_sbo_id(sbo.data[key])    

    #create sbo
    @classmethod
    def create_sbo(cls, input_db_dir, **files):
        Onto.correction_of_SBO_OBO_file(input_db_dir, files["sbo_data"], 'SBO_out_test.obo')
        ontology = Onto.create_ontology_from_owl(input_db_dir, 'SBO_out_test.obo')
        list_sbo = Onto.parse_sbo_terms_from_ontology(ontology)

        sbos = [cls(data = dict_) for dict_ in list_sbo]
        cls.insert_sbo_id(sbos,"id")
        cls.insert_name(sbos, "name")
        cls.insert_definition(sbos, "definition")

        return(list_sbo)

    class Meta():
        table_name = 'sbo'