import sys
import os
import unittest

from biota.ontology import Ontology
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel, ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked
from chebi.chebi import Chebi

####################################################################################
#
# Chebi ontology class
#
####################################################################################
 
class Chebi_Ontology(Ontology):
    chebi_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    #definition = CharField(null=True, index=True)
    #xrefs = CharField(null=True, index=True)
    _table_name = 'chebiOntology'

    #Setters
    def set_chebi_id(self, id):
        self.chebi_id = id
    
    def set_name(self, name):
        self.name = name
    
    #Inserts
    def insert_chebi_id(list__, key):
        for chebs in list__:
            chebs.set_chebi_id(chebs.data[key])

    def insert_name(list__, key):
        for chebs in list__:
            chebs.set_name(chebs.data[key])

    @classmethod
    def create_chebis(cls, input_db_dir, **files):
        onto = Chebi.create_ontology_from_file(input_db_dir, files['chebi_data'])
        list_chebi = Chebi.parse_onto_from_ontology(onto)
        chebis = [cls(data = dict_) for dict_ in list_chebi]
        cls.insert_chebi_id(chebis, "id")
        cls.insert_name(chebis, "name")
        return(list_chebi)

    class Meta():
        table_name = 'chebiOntology'

class ChebiOntologyJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"chebi_id": {{view_model.model.chebi_id}} , "name": {{view_model.model.name}}, "definition": {{view_model.model.data.definition}} }')