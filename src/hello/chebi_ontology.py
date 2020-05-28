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
    xrefs = CharField(null=True, index=True)
    _table_name = 'chebi_ontology'

    def set_chebi_id(self, id):
        self.chebi_id = id
    
    def set_name(self, name):
        self.name = name
    
    def set_definition(self, def_):
        self.definition = def_
    
    def set_xrefs(self, xrefs_):
        self.xrefs = xrefs_ 

    def create_chebis(self, list_chebi):
        #for dict_ in list_chebi:
            #chebis = [Chebi_Ontology(data = dict_)]
        chebis = [Chebi_Ontology(data = dict_) for dict_ in list_chebi]
        #for chebs in chebis:
            #chebs.set_chebi_id = chebs['id']
            #chebs.set_name = chebs['name']
            #chebs.set_definition = chebs['definition']
        status = 'test ok'
        return(status)

class Meta():
    table_name = 'chebi_ontology'
