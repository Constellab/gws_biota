import unittest #not sure if necessary
import copy #not sure if necessary
import sys
import os
import unittest

from gws.prism.app import App
from gws.prism.model import Process
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from gws.prism.controller import Controller
from taxo.taxonomy import Taxo
from peewee import IntegerField, DateField, DateTimeField, CharField, ForeignKeyField

from pronto import Ontology as Ont, Xref, SynonymType, Subset, PropertyValue, LiteralPropertyValue


####################################################################################
#
# Taxonomy class
#
####################################################################################
class Taxonomy(Resource):
    tax_id = CharField(null=True, index=True)
    name = CharField(null=True, index=True)
    rank = CharField(null=True, index=True)
    _table_name = 'taxonomy'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


     #setter functions
    def set_tax_id(self, tax_id__):
        self.tax_id = tax_id__
    
    def set_name(self, name__):
        self.name = name__

    def set_rank(self, rank__):
        self.rank = rank__

    #insert function
    def insert_tax_id(list__, key):
        for comp in list__:
            comp.set_tax_id(comp.data[key])

    def insert_name(list__, key):
        for comp in list__:
            comp.set_name(comp.data[key])

    def insert_rank(list__, key):
        for comp in list__:
            comp.set_rank(comp.data[key])

    @classmethod
    def create_taxons_from_list(cls):
        list_taxons = Taxo.parse_taxonomy_from_ncbi('Sphingomonadaceae')
        taxons = [cls(data = d) for d in list_taxons]
        cls.insert_tax_id(taxons, 'tax_id')
        cls.insert_name(taxons, 'name')
        cls.insert_rank(taxons, 'rank')
        status = 'ok'
        return(status)


    class Meta():
        table_name = 'taxonomy'