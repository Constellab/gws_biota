import os, sys
from gena.protein import Protein 
from gena.taxonomy import Taxonomy as Tax
from gena.bto import BTO as BT
from brenda.brenda import Brenda

from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager

from peewee import CharField, Model, chunked, ForeignKeyField, ManyToManyField

import logging
from collections import OrderedDict
from brendapy import BrendaParser, BrendaProtein
from brendapy import utils
from brendapy.taxonomy import Taxonomy
from brendapy.tissues import BTO
from brendapy.substances import CHEBI

####################################################################################
#
# Enzyme class
#
####################################################################################

class Enzyme(Protein):
    ec = CharField(null=True, index=True)
    organism = CharField(null=True, index=True)
    taxonomy = ForeignKeyField(Tax, backref = 'taxonomy', null = True)
    tissue_id = ForeignKeyField(BT, backref='blood tissue taxonomy', null = True)
    uniprot_id = CharField(null=True, index=True)
    _table_name = 'enzyme'

    #Setters
    def set_ec(self, ec__):
        self.ec = ec__
    
    def set_organism(self, organism__):
        self.organism = organism__

    def set_taxonomy(self):
        if(self.data['taxonomy'] != None):
            try:
                tax = Tax.get(Tax.tax_id == str(self.data['taxonomy']))
                self.taxonomy = tax
            except:
                print("did not found the tax_id: " + str(self.data['taxonomy']))
    
    def set_tissue(self):
        if('st' in self.data.keys()):
            try:
                bto = BT.get(BT.bto_id == self.data['st'])
                self.tissue_id = bto
            except:
                print("did not found the bto_id:" + self.data['st'])
    
    def set_uniprot_id(self, uniprot_id__):
        self.uniprot_id = uniprot_id__

    #Inserts
    def insert_protein_id(list__, key):
        for comp in list__:
            comp.set_protein_id(comp.data[key])

    def insert_ec(list__, key):
        for comp in list__:
            comp.set_ec(comp.data[key])

    def insert_organism(list__, key):
        for comp in list__:
            comp.set_organism(comp.data[key])
    """
    def insert_taxonomy(list__, key):
        for comp in list__:
            comp.set_taxonomy(comp.data[key])
    """

    def insert_uniprot_id(list__, key):
        for comp in list__:
            comp.set_uniprot_id(comp.data[key])
            
    @classmethod
    def create_enzymes_from_dict(cls, input_db_dir, **files):
        brenda = Brenda(os.path.join(input_db_dir, files['brenda_file']))
        list_proteins = brenda.parse_all_protein_to_dict()
        list_dict = []
        list_chemical_info = ['in','lo','me','mw','nsp','pho','phr','phs','pm','to','tr','ts', 'st']
        for d in list_proteins:
            dict_enz = {}
            dict_enz['ec'] = d['ec']
            dict_enz['taxonomy'] = d['taxonomy']
            dict_enz['organism'] = d['organism']
            dict_enz['uniprot'] = d['uniprot']
            dict_enz['name'] = d['name']
            for info in list_chemical_info:
                if(info in d.keys()):
                    dict_enz[info]= d[info]
            list_dict.append(dict_enz)
        enzymes = [cls(data = dict_) for dict_ in list_dict]
        cls.insert_ec(enzymes, 'ec')
        cls.insert_organism(enzymes, 'organism')
        cls.insert_uniprot_id(enzymes, 'uniprot')
        for enz in enzymes:
            #enz.save()
            enz.set_taxonomy()
            enz.set_tissue()
        return(list_dict)
    
    class Meta():
        table_name = 'enzymes'
    
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
