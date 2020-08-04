# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, FloatField

from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate
from gws.prism.model import ResourceViewModel

from biota.db.entity import Entity

class Compound(Entity):
    """
    This class represents metabolic compounds from the ChEBI database.
    
    Chemical Entities of Biological Interest (ChEBI) includes an
    ontological classification, whereby the relationships between molecular 
    entities or classes of entities and their parents and/or children are 
    specified (https://www.ebi.ac.uk/chebi/). ChEBI data are available under the Creative Commons License (CC BY 4.0),
    https://creativecommons.org/licenses/by/4.0/

    :property name : name of the compound
    :type name : CharField
    :property chebi_id: chebi accession number
    :type chebi_id: CharField
    :property formula: chimical formula
    :type formula: CharField
    :property mass: mass of the compound
    :type mass: FloatField 
    :property charge: charge of the compound
    :type charge: FloatField
    """
    
    name = CharField(null=True, index=True)
    chebi_id = CharField(null=True, index=True)
    formula = CharField(null=True, index=True)
    mass = FloatField(null=True, index=True)
    charge = FloatField(null=True, index=True)
    _table_name = 'compound'

    # -- C -- 
    @classmethod
    def create_compound_db(cls, biodata_db_dir, **files):
        """
        Creates and fills the `compound` database

        :param biodata_db_dir: path of the :file:`go.obo`
        :type biodata_db_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """

        from biota._helper.chebi import Chebi as ChebiHelper

        list_comp = ChebiHelper.parse_csv_from_file(biodata_db_dir, files['chebi_compound_file'])
        compounds = cls._create_compounds(list_comp)
        cls.save_all(compounds)

        list_chemical = ChebiHelper.parse_csv_from_file(biodata_db_dir, files['chebi_chemical_data_file'])
        cls._set_chemicals(list_chemical)
        cls.save_all(compounds)



    @classmethod
    def _create_compounds(cls, list_compound):
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
            comp.name =  comp.data["name"]
            comp.chebi_id = comp.data["chebi_accession"]

        return compounds

    # -- S --

    def set_name(self, name):
        self.name = name
    
    def set_chebi_id(self, chebi_id):
        self.chebi_id = chebi_id
    
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
                    comp = cls.get(cls.chebi_id == 'CHEBI:' + chem['compound_id'])
                    comp.set_formula(chem['chemical_data'])
                except:
                    pass
                    #print('can not find the compound CHEBI:' + str(chem['compound_id'] + ' to set formula'))

            elif(chem['type'] == 'MASS'):
                try:
                    comp = cls.get(cls.chebi_id == 'CHEBI:' + chem['compound_id'])
                    comp.set_mass(float(chem['chemical_data']))
                except:
                    pass
                    #print('can not find the compound CHEBI:' + str(chem['compound_id'] + ' to set mass'))
                
            elif(chem['type'] == 'CHARGE'):
                try:
                    comp = cls.get(cls.chebi_id == 'CHEBI:' + chem['compound_id'])
                    comp.set_charge(float(chem['chemical_data']))
                except:
                    pass
                    #print('can not find the compound CHEBI:' + str(chem['compound_id']) + ' to set charge')

    class Meta:
        table_name = 'compound'

class CompoundJSONStandardViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.chebi_id}},
            "name": {{view_model.model.name}},
            }
        """)

class CompoundJSONPremiumViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "id": {{view_model.model.chebi_id}},
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

Controller.register_model_classes([Compound])
