import os, sys
from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel
from biota.prism.entity import Entity
from biota.helper.chebi import Chebi
from peewee import CharField, FloatField


####################################################################################
#
# Compound class
#
####################################################################################

class Compound(Entity):
    """

    This class allows to load chebi compound entities in the database
    
    chebi compound entities are automatically created by the create_go() method

    :type go_id: CharField 
    :property go_id: id of the go term
    :type name: CharField 
    :property name: name of the go term
    :type namespace: CharField 
    :property namespace: namespace of the go term

    """
    name = CharField(null=True, index=True)
    source_accession = CharField(null=True, index=True)
    formula = CharField(null=True, index=True)
    mass = FloatField(null=True, index=True)
    charge = FloatField(null=True, index=True)
    _table_name = 'compound'

    # -- C -- 
    @classmethod
    def create_compounds_from_files(cls, input_db_dir, **files):
        list_comp = Chebi.parse_csv_from_file(input_db_dir, files['chebi_compound_file'])
        compounds = cls.create_compounds(list_comp)
        cls.save_all(compounds)

        list_chemical = Chebi.parse_csv_from_file(input_db_dir, files['chebi_chemical_data_file'])
        cls._set_chemicals(list_chemical)
        cls.save_all(compounds)

        return list_comp

    @classmethod
    def create_compounds(cls, list_compound):
        compounds = [cls(data = dict_) for dict_ in list_compound]
        for comp in compounds:
            comp.set_name( comp.data["name"] )
            comp.set_source_accession( comp.data["chebi_accession"] )

        return compounds

    # -- S --

    def set_name(self, name):
        self.name = name
    
    def set_source_accession(self, source_accession):
        self.source_accession = source_accession
    
    def set_formula(self, formula):
        self.formula = formula
    
    def set_mass(self, mass):
        self.mass = mass
    
    def set_charge(self, charge):
        self.charge = charge

    @classmethod
    def set_reactions_from_list(cls, list_reaction):
        for dict_ in list_reaction:
            if ('entry' in dict_.keys()):
                try:
                    comp = cls.get(cls.source_accession == dict_["entry"])
                    comp.set_reactions(dict_['reaction'])
                except:
                    pass
                    #print('can not find the compound ' + str(dict_["entry"]) + ' to set reactions')
        
    @classmethod
    def _set_chemicals(cls, list_chemical):
        for chem in list_chemical:
            if(chem['type'] == 'FORMULA'):
                try:
                    comp = cls.get(cls.source_accession == 'CHEBI:' + chem['compound_id'])
                    comp.set_formula(chem['chemical_data'])
                except:
                    pass
                    #print('can not find the compound CHEBI:' + str(chem['compound_id'] + ' to set formula'))

            elif(chem['type'] == 'MASS'):
                try:
                    comp = cls.get(cls.source_accession == 'CHEBI:' + chem['compound_id'])
                    comp.set_mass(float(chem['chemical_data']))
                except:
                    pass
                    #print('can not find the compound CHEBI:' + str(chem['compound_id'] + ' to set mass'))
                
            elif(chem['type'] == 'CHARGE'):
                try:
                    comp = cls.get(cls.source_accession == 'CHEBI:' + chem['compound_id'])
                    comp.set_charge(float(chem['chemical_data']))
                except:
                    pass
                    #print('can not find the compound CHEBI:' + str(chem['compound_id']) + ' to set charge')

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




