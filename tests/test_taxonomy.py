import sys
import os
import unittest

from gws.settings import Settings
from biota.taxonomy import Taxonomy, TaxonomyJSONStandardViewModel, TaxonomyJSONPremiumViewModel

############################################################################################
#
#                                        TestTaxonomy
#                                         
############################################################################################
settings = Settings.retrieve()
test_data_path = settings.get_data("biota_test_data_dir")

class TestGO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        Taxonomy.drop_table()
        Taxonomy.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Taxonomy.drop_table()
        pass
    
    def test_db_object(self):

        files_test = dict(
            nodes = "nodes_test.dmp",
            names = "names_test.dmp",
            division = "division.dmp",
            citations = "citations.dmp"
        )
        Taxonomy.create_taxons(test_data_path, bulk_size = 10, **files_test)
        #self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 72).data, {'tax_id': '72', 'ancestor': '71', 'rank': 'species', 'division': 'Bacteria'})
        
        """
        # --------- Testing views --------- #
        tax1 = Taxonomy.get(Taxonomy.tax_id == 9593)
        
        tax1_standard_view_model = TaxonomyJSONStandardViewModel(tax1)
        tax1_premium_view_model = TaxonomyJSONPremiumViewModel(tax1)
        
        view1 = tax1_standard_view_model.render()
        view2 = tax1_premium_view_model.render()
        """
        # self.assertEqual(view1,"""
        #     {
        #     "id": 9593,
        #     "name": Gorilla gorilla,
        #     }
        # """)

        # self.assertEqual(view2,"""
        #     {
        #     "id": 9593,
        #     "name": Gorilla gorilla,
        #     "rank": species,
        #     "ancestor": 9592,
        #     }
        # """)
        