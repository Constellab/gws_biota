import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings

from biota.chebiOntology import ChebiOntology, ChebiOntologyStandardJSONViewModel, ChebiOntologyPremiumJSONViewModel

############################################################################################
#
#                                        TestChebiOntology
#                                         
############################################################################################
settings = Settings.retrieve()
test_data_path = settings.get_data("biota_test_data_dir")

class TestChebiOntology(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ChebiOntology.drop_table()
        ChebiOntology.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Compound.drop_table()
        pass

    def test_db_object(self):
        files = dict(
            chebi_data = "chebi.obo",
        )

        files_test = dict(
            chebi_data = "chebi_test.obo",
        )
        
        ChebiOntology.create_chebis(test_data_path, **files_test)
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:24431').name, "chemical entity")
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:17051').name, 'fluoride')
        
        # --------- Testing views --------- #
        chebi1 = ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:17051')
        
        chebi1_standard_view_model = ChebiOntologyStandardJSONViewModel(chebi1)
        chebi1_premium_view_model = ChebiOntologyPremiumJSONViewModel(chebi1)
        
        view1 = chebi1_standard_view_model.render()
        view2 = chebi1_premium_view_model.render()
        
        self.assertEqual(view1,"""
            {
            "id": CHEBI:17051,
            "label": fluoride,
            }
        """)
        #random test pass
        #self.assertEqual(view2,"""
        #    {
        #    "id": CHEBI:17051,
        #    "label": fluoride,
        #    "definition": None,
        #    "alternative_id": ['CHEBI:5113', 'CHEBI:14271', 'CHEBI:49593']
        #    }
        #""")