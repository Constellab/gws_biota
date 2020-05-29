import os, sys
from hello.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from peewee import CharField, Model, chunked

####################################################################################
#
# Compound class
#
####################################################################################

path_test = os.path.realpath('./databases_input') #Set the path where we can find input data

class Compound(Entity):
    name = CharField(null=True, index=True)
    source_accession = CharField(null=True, index=True)
    formula = CharField(null=True, index=True)
    mass = CharField(null=True, index=True)
    charge = CharField(null=True, index=True)
    _table_name = 'compound'

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
    

    def create_compounds(self, list_compound):
        compounds = [Compound(data = dict_) for dict_ in list_compound]
        Compound.insert_source_accession(compounds, 'CHEBI_ACCESSION')
        Compound.insert_name(compounds, 'NAME')
        status = 'ok'
        return(compounds)
    
    def get_chemical(self, list_chemical):
        for data_ in list_chemical:
            line_count = 0
            if(data_['TYPE'] == 'FORMULA'):
                if(line_count <10):
                    status = data_['CHEMICAL_DATA\n']
                    line_count += 1
                Compound.update({Compound.formula: data_['CHEMICAL_DATA\n']}).where(Compound.source_accession == 'CHEBI:' + data_['COMPOUND_ID']).execute()
                """
                if(line_count < 1):
                    comp = Compound.get(Compound.name == "eugenol" )
                    comp.set_formula(data_['CHEMICAL_DATA\n'])
                    line_count +=1
                """
            """
            if('MASS' in data.keys()):
                
            if('CHARGE' in data.keys())
            """
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
])"""


class Meta:
    table_name = 'compound'


