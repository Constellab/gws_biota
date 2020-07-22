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
    
    chebi compound entities are automatically created by the create_compounds_from_files() method

    :type name : CharField
    :property name : name of the compound
    :type source_accession: CharField
    :property source_accession: chebi accession number
    :type formula: CharField
    :property formula: chimical formula
    :type mass: FloatField 
    :property mass: mass of the compound
    :type charge: FloatField
    :property charge: charge of the compound

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
        """
        Creates and registers chebi compound entities in the database
        Use the chebi helper of biota to get all chebi compound in a list
        Creates compounds by calling create_compounds() method
        Collects chemical informations about chebi compounds and set their chemical 
        attribute by calling the _set_chemicals() method
        Register compounds by calling the save_all() method 

        :type input_db_dir: str
        :param input_db_dir: path to the folder that contain the go.obo file
        :type files: dict
        :param files: dictionnary that contains all data files names
        :returns: None
        :rtype: None

        """
        list_comp = Chebi.parse_csv_from_file(input_db_dir, files['chebi_compound_file'])
        compounds = cls.create_compounds(list_comp)
        cls.save_all(compounds)

        list_chemical = Chebi.parse_csv_from_file(input_db_dir, files['chebi_chemical_data_file'])
        cls._set_chemicals(list_chemical)
        cls.save_all(compounds)



    @classmethod
    def create_compounds(cls, list_compound):
        """

        Creates chebi compound from a list 

        :type list_compound: list
        :param list_compound: list of dictionnaries where each element refers 
        to a chebi compound
        :returns: list of Compound entities
        :rtype: list

        """
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
    def _set_chemicals(cls, list_chemical):
        """
        
        Sets chemical informations of compound from a tsv file which contains 
        chebi chemical informations such as mass, chemical formula of charge

        :type list_chemical: list 
        :param list_chemical: list of chemical informations in the tsv file, 
        each element represent one informations about formula, mass or charge of a 
        chebi compound 
        :returns: None

        """
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




