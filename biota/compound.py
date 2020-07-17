import os, sys
from biota.entity import Entity
from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel
from peewee import CharField, FloatField

from chebi.chebi import Chebi

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
    _table_name = 'compound'

    # setters
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


    # inserts
    @classmethod
    def insert_name(cls, list__, key):
        for comp in list__:
            comp.set_name(comp.data[key])

    @classmethod
    def insert_source_accession(cls, list__, key):
        for comp in list__:
            comp.set_source_accession(comp.data[key])

    @classmethod
    def insert_formula(cls, list__, key):
        for comp in list__:
            comp.set_formula(key)
    
    @classmethod
    def insert_mass(cls, list__, key):
        for comp in list__:
            comp.set_mass(comp.data[key])

    @classmethod
    def insert_charge(cls, list__, key):
        for comp in list__:
            comp.set_charge(comp.data[key])

    # create
    @classmethod
    def create_compounds_from_files(cls, input_db_dir, **files):
        list_comp = Chebi.parse_csv_from_file(input_db_dir, files['chebi_compound_file'])
        cls.create_compounds(list_comp)
        cls.save_all()

        list_chemical = Chebi.parse_csv_from_file(input_db_dir, files['chebi_chemical_data_file'])
        cls.set_chemicals(list_chemical)
        cls.save_all()

        return(list_comp)

    @classmethod
    def create_compounds(cls, list_compound):
        compounds = [cls(data = dict_) for dict_ in list_compound]
        cls.insert_source_accession(compounds, 'chebi_accession')
        cls.insert_name(compounds, 'name')
        return(compounds)
    
    @classmethod
    def set_chemicals(cls, list_chemical):
        for data_ in list_chemical:
            if(data_['type'] == 'FORMULA'):
                try:
                    comp = cls.get(cls.source_accession == 'CHEBI:' + data_['compound_id'])
                    comp.set_formula(data_['chemical_data'])
                except:
                    print('can not find the compound CHEBI:' + str(data_['compound_id'] + ' to set formula'))

            elif(data_['type'] == 'MASS'):
                try:
                    comp = cls.get(cls.source_accession == 'CHEBI:' + data_['compound_id'])
                    comp.set_mass(float(data_['chemical_data']))
                except:
                    print('can not find the compound CHEBI:' + str(data_['compound_id'] + ' to set mass'))
                
            elif(data_['type'] == 'CHARGE'):
                try:
                    comp = cls.get(cls.source_accession == 'CHEBI:' + data_['compound_id'])
                    comp.set_charge(float(data_['chemical_data']))
                except:
                    print('can not find the compound CHEBI:' + str(data_['compound_id']) + ' to set charge')
        status = 'ok'
        return(status)
   
    @classmethod
    def set_reactions_from_list(cls, list_reaction):
        for dict_ in list_reaction:
            if ('entry' in dict_.keys()):
                try:
                    comp = cls.get(cls.source_accession == dict_["entry"])
                    comp.set_reactions(dict_['reaction'])
                except:
                    print('can not find the compound ' + str(dict_["entry"]) + ' to set reactions')
        status = 'ok'
        return(status)

    class Meta:
        table_name = 'compound'

class CompoundJSONStandardViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.source_accession}},
            "name": {{view_model.model.name}},
            }
        """)

class CompoundJSONPremiumViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.source_accession}},
            "name": {{view_model.model.name}},
            "source": {{view_model.model.data["source"]}},
            "formula": {{view_model.model.formula}},
            "mass": {{view_model.model.mass}},
            "charge": {{view_model.model.charge}},
            "definition": {{view_model.model.data["definition"]}},
            "status": {{view_model.model.data["status"]}},
            "created by": {{view_model.model.data["created_by"]}},
            "star": {{view_model.model.data["star"]}}
            }
        """)




