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
# BTO class
#
####################################################################################

class BTO(Ontology):
    bto_id = CharField(null=True, index=True)
    label = CharField(null=True, index=True)
    ancestors = CharField(null=True, index=True)
    _table_name = 'bto'

    #setters
    def set_bto_id(self, id):
        self.bto_id = id

    def set_label(self, label_):
        self.label = label_ 
    
    def set_ancestors(self, list_ancestors):
        self.ancestors = list_ancestors

    #insert functions
    def insert_bto_id(list__, key):
        for bto in list__:
            bto.set_bto_id(bto.data[key]) 

    def insert_label(list__, key):
        for bto in list__:
            bto.set_label(bto.data[key]) 

    def insert_ancestors(list__, key):
        for bto in list__:
            bto.set_ancestors(bto.data[key]) 
    
    #create bto
    @classmethod
    def create_bto(cls, input_db_dir, **files):
        list_bto = Onto.parse_bto_from_json(input_db_dir, files['bto_json_data'])
        btos = [cls(data = dict_) for dict_ in list_bto]
        cls.insert_bto_id(btos,"id")
        cls.insert_label(btos, "label")
        cls.insert_ancestors(btos, "ancestors")
        status = 'ok'
        return(status)


    class Meta():
        table_name = 'bto'