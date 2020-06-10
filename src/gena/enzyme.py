import os, sys
from gena.protein import Protein 
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked
from collections import OrderedDict
from brendapy import BrendaParser, BrendaProtein
from brendapy.taxonomy import Taxonomy

####################################################################################
#
# Enzyme class
#
####################################################################################

path_test = os.path.realpath('./databases_input') #Set the path where we can find input data

class Enzyme(Protein):
    protein_id = CharField(null=True, index=True)
    ec = CharField(null=True, index=True)
    organism = CharField(null=True, index=True)
    taxonomy = CharField(null=True, index=True)
    uniprot_id = CharField(null=True, index=True)
    _table_name = 'enzyme'
    pass

    class Meta():
        table_name = 'enzymes'

    #setter functions
    def set_protein_id(self, id__):
        self.protein_id = id__

    def set_ec(self, ec__):
        self.ec = ec__
    
    def set_organism(self, organism__):
        self.organism = organism__

    def set_taxonomy(self, taxonomy__):
        self.taxonomy = taxonomy__

    def set_uniprot_id(self, uniprot_id__):
        self.uniprot_id = uniprot_id__

    #insert function
    def insert_protein_id(list__, key):
        for comp in list__:
            comp.set_protein_id(comp.data[key])

    def insert_ec(list__, key):
        for comp in list__:
            comp.set_ec(comp.data[key])

    def insert_organism(list__, key):
        for comp in list__:
            comp.set_organism(comp.data[key])

    def insert_taxonomy(list__, key):
        for comp in list__:
            comp.set_taxonomy(comp.data[key])

    def insert_uniprot_id(list__, key):
        for comp in list__:
            comp.set_uniprot_id(comp.data[key])
            
    @classmethod
    def create_enzymes(cls, list_proteins):
        list_dict = []
        for p in list_proteins:
            dict_enz = {}
            dict_enz['protein_id'] = p.protein_id
            dict_enz['ec'] = p.ec
            dict_enz['taxonomy'] = p.taxonomy
            dict_enz['organism'] = p.organism
            dict_enz['uniprot'] = p.uniprot
            dict_enz['AC'] = p.AC
            dict_enz['KM'] = p.KM
            dict_enz['TO'] = p.TO
            list_dict.append(dict_enz)
        enzymes = [cls(data = dict_) for dict_ in list_dict]
        cls.insert_protein_id(enzymes, 'protein_id')
        cls.insert_ec(enzymes, 'ec')
        cls.insert_taxonomy(enzymes, 'taxonomy')
        cls.insert_organism(enzymes, 'organism')
        cls.insert_uniprot_id(enzymes, 'uniprot')
        status = 'ok'
        return(status)
    
class EnzymeHTMLViewModel(ResourceViewModel):
    template = HTMLViewTemplate("ID: {{view_model.model.data.ID}}")

class EnzymeJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id":"{{view_model.model.data.ID}}"}')
"""
Enzyme.register_view_models([
    EnzymeHTMLViewModel, 
    EnzymeJSONViewModel
])

Controller.register_models([
    Enzyme,
    EnzymeHTMLViewModel,
    EnzymeJSONViewModel
])
"""
