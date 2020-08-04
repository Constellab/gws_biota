import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings

from biota.db.chebi_ontology import ChebiOntology, ChebiOntologyJSONViewModel, ChebiOntologyPremiumJSONViewModel

############################################################################################
#
#                                        TestChebiOntology
#                                         
############################################################################################
settings = Settings.retrieve()
testdata_path = settings.get_data("biota:chebi_biodata_dir")

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

        files_test = dict(
            chebi_file = "./obo_original/chebi.obo",
        )
        
        ChebiOntology.create_chebi_ontology_db(testdata_path, **files_test)
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:24431').name, "chemical entity")
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:17051').name, 'fluoride')
        
        # --------- Testing views --------- #
        chebi = ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:17051')
        chebi_standard_view_model = ChebiOntologyJSONViewModel(chebi)
        view = chebi_standard_view_model.render()
        
        self.assertEqual(view,"""
            {
            "id": CHEBI:17051,
            "label": fluoride,
            }
        """)
