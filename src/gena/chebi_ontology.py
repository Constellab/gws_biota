import sys
import os
import unittest

from gena.ontology import Ontology
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

    class Meta():
        table_name = 'chebi_ontology'

    def set_chebi_id(self, id):
        self.chebi_id = id
    
    def set_name(self, name):
        self.name = name
    
    #def set_xrefs(self, xrefs_):
        #self.xrefs = xrefs_ 

    def insert_chebi_id(list__, key):
        for chebs in list__:
            chebs.set_chebi_id(chebs.data[key])

    def insert_name(list__, key):
        for chebs in list__:
            chebs.set_name(chebs.data[key])


    @classmethod
    def create_chebis(cls, list_chebi):
        chebis = [cls(data = dict_) for dict_ in list_chebi]
        cls.insert_chebi_id(chebis, "id")
        cls.insert_name(chebis, "name")
        status = 'test ok'
        return(status)
