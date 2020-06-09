import os, sys
from gena.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked
from gena.ontology import Ontology
from peewee import CharField, chunked
from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue

####################################################################################
#
# SBO class
#
####################################################################################

class SBO(Ontology):
    sbo_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    _table_name = 'sbo'
    
    #setters
    def set_sbo_id(self, id):
        self.sbo_id = id

    def set_name(self, name__):
        self.name = name__

    #insert functions
    def insert_sbo_id(list__, key):
        for sbo in list__:
            sbo.set_sbo_id(sbo.data[key])

    def insert_name(list__, key):
        for sbo in list__:
            sbo.set_name(sbo.data[key])

    #create sbo
    @classmethod
    def create_sbo(cls, list_sbo_):
        sbos = [cls(data = dict_) for dict_ in list_sbo_]
        cls.insert_sbo_id(sbos,"id")
        cls.insert_name(sbos, "name")
        #GO.insert_namespace(gos, "namespace")
        #GO.insert_definition(gos, "definition")
        status = 'ok'
        return(status)

    class Meta():
        table_name = 'sbo'