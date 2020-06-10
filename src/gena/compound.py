import os, sys
from gena.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, FloatField, Model, chunked

####################################################################################
#
# Compound class
#
####################################################################################

class Compound(Entity):
    name = CharField(null=True, index=True)
    source_accession = CharField(null=True, index=True)
    formula = CharField(null=True, index=True)
    mass = FloatField(null=True, index=True)
    charge = FloatField(null=True, index=True)
    reactions = CharField(null=True, index=True)
    _table_name = 'compound'

    class Meta:
        table_name = 'compounds'

    #setter functions
    def set_name(self, name__):
        self.name = name__
    
    def set_source_accession(self, source_accession__):
        self.source_accession = source_accession__
    
    def set_formula(self, formula__):
        self.formula = formula__
    
    def set_mass(self, mass__):
        self.mass = mass__
    
    def set_charge(self, charge__):
        self.charge = charge__
    
    def set_reactions(self, reactions__):
        self.reactions = reactions__

    #insert function
    def insert_name(list__, key):
        for comp in list__:
            comp.set_name(comp.data[key])

    def insert_source_accession(list__, key):
        for comp in list__:
            comp.set_source_accession(comp.data[key])

    def insert_formula(list__, key):
        for comp in list__:
            comp.set_formula(key)
    
    def insert_mass(list__, key):
        for comp in list__:
            comp.set_mass(comp.data[key])

    def insert_charge(list__, key):
        for comp in list__:
            comp.set_charge(comp.data[key])

    def insert_reactions(list__, key):
        for comp in list__:
            comp.set_reactions(comp.data[key])

    @classmethod
    def create_compounds(cls, list_compound):
        compounds = [cls(data = dict_) for dict_ in list_compound]
        cls.insert_source_accession(compounds, 'chebi_accession')
        cls.insert_name(compounds, 'name')
        status = 'ok'
        return(compounds)
    
    @classmethod
    def set_chemicals(cls, list_chemical):
        for data_ in list_chemical:
            if(data_['type'] == 'FORMULA'):
                try:
                    comp = cls.get(cls.source_accession == 'CHEBI:' + data_['compound_id'])
                    comp.set_formula(data_['chemical_data'])
                except:
                    print('can not find the compound CHEBI:' + str(data_['compound_id']))

            elif(data_['type'] == 'MASS'):
                try:
                    comp = cls.get(cls.source_accession == 'CHEBI:' + data_['compound_id'])
                    comp.set_mass(float(data_['chemical_data']))
                except:
                    print('can not find the compound CHEBI:' + str(data_['compound_id']))
                
            elif(data_['type'] == 'CHARGE'):
                try:
                    comp = cls.get(cls.source_accession == 'CHEBI:' + data_['compound_id'])
                    comp.set_charge(float(data_['chemical_data']))
                except:
                    print('can not find the compound CHEBI:' + str(data_['compound_id']))
        status = 'ok'
        return(status)
   
    @classmethod
    def set_reactions(cls, list_reaction):
        for dict_ in list_reaction:
            if ("entry" in dict_.keys()):
                try:
                    comp = cls.get(cls.source_accession == dict_["entry"])
                    comp.set_reactions(dict_['reaction'])
                except:
                    print('can not find the compound CHEBI:' + str(dict_["entry"]))
        status = 'ok'
        return(status)


class CompoundHTMLViewModel(ResourceViewModel):
    template = HTMLViewTemplate("ID: {{view_model.model.data.ID}}")

class CompoundJSONViewModel(ResourceViewModel):
    template = JSONViewTemplate('{"id":"{{view_model.model.data.ID}}"}')
"""
Compound.register_view_models([
    CompoundHTMLViewModel, 
    CompoundJSONViewModel
])

Controller.register_models([
    Compound,
    CompoundHTMLViewModel,
    CompoundJSONViewModel
])
"""



