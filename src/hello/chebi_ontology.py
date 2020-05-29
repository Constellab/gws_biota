import sys
import os
import unittest

from hello.ontology import Ontology
from chebs.obo_parser import create_ontology_from_file, obo_parser_from_ontology
from peewee import CharField, Model, chunked
from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

####################################################################################
#
# Chebi ontology class
#
####################################################################################
path_test = os.path.realpath('./databases_input') #Set the path where we can find input data

class Chebi_Ontology(Ontology):
    chebi_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    definition = CharField(null=True, index=True)
    #xrefs = CharField(null=True, index=True)
    _table_name = 'chebi_ontology'

    def set_chebi_id(self, id):
        self.chebi_id = id
    
    def set_name(self, name):
        self.name = name
    
    def set_definition(self, def_):
        self.definition = def_
    
    #def set_xrefs(self, xrefs_):
        #self.xrefs = xrefs_ 

    def insert_chebi_id(list__, key):
        for chebs in list__:
            chebs.set_chebi_id(chebs.data[key])

    def insert_name(list__, key):
        for chebs in list__:
            chebs.set_name(chebs.data[key])

    def insert_defintion(list__, key):
        for chebs in list__:
            chebs.set_definition(chebs.data[key])

    def create_chebis(self, list_chebi):
        #for dict_ in list_chebi:
            #chebis = [Chebi_Ontology(data = dict_)]
        chebis = [Chebi_Ontology(data = dict_) for dict_ in list_chebi]
        Chebi_Ontology.insert_chebi_id(chebis, "id")
        Chebi_Ontology.insert_name(chebis, "name")
        Chebi_Ontology.insert_defintion(chebis, "definition")
        status = 'test ok'
        return(status)

class Meta():
    table_name = 'chebi_ontology'
