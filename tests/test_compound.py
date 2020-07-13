import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings
from biota.compound import Compound, CompoundJSONStandardViewModel, CompoundJSONPremiumViewModel

############################################################################################
#
#                                        TestCompound
#                                         
############################################################################################
settings = Settings.retrieve()
test_data_path = settings.get_data("biota_test_data_path")

class TestCompound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Compound.drop_table()
        Compound.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Compound.drop_table()
        pass

    def test_db_object(self):
        files = dict(
            chebi_compound_file = "compounds.tsv",
            chebi_chemical_data_file =  "chemical_data.tsv",
            #rhea_kegg_compound_file =  "rhea-kegg.compound"
        )

        files_test = dict(
            chebi_compound_file = "compounds_test.tsv",
            chebi_chemical_data_file =  "chemical_data_test.tsv",
            #rhea_kegg_compound_file =  "rhea-kegg-test.compound"
        )

        Compound.create_compounds_from_files(test_data_path, **files_test)
        Controller.save_all()
        self.assertEqual(Compound.get(Compound.source_accession == 'CHEBI:58321').name, 'L-allysine zwitterion')
        self.assertEqual(Compound.get(Compound.source_accession == 'CHEBI:59789').name, 'S-adenosyl-L-methionine zwitterion')
        
        # --------- Testing views --------- #
        comp1 = Compound.get(Compound.source_accession == 'CHEBI:58321')
        
        comp1_standard_view_model = CompoundJSONStandardViewModel(comp1)
        comp1_premium_view_model = CompoundJSONPremiumViewModel(comp1)
        
        view2 = comp1_premium_view_model.render()
        view1 = comp1_standard_view_model.render()

        self.assertEqual(view1,"""
            {
            "id": CHEBI:58321,
            "name": L-allysine zwitterion,
            }
        """)

        self.assertEqual(view2,"""
            {
            "id": CHEBI:58321,
            "name": L-allysine zwitterion,
            "source": Rhea,
            "formula": None,
            "mass": None,
            "charge": None,
            "definition": ,
            "status": C,
            "created by": ,
            "star": 
            }
        """)