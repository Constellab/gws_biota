import sys
import os
import unittest

from gws.settings import Settings
from biota.db.taxonomy import Taxonomy

############################################################################################
#
#                                        TestTaxonomy
#                                         
############################################################################################
settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestGO(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Taxonomy.drop_table()
        Taxonomy.create_table()
   
    @classmethod
    def tearDownClass(cls):
        Taxonomy.drop_table()
        pass
    
    def test_db_object(self):

        params = dict(
            biodata_dir = testdata_path,
            ncbi_node_file = "nodes_test.dmp",
            ncbi_name_file = "names_test.dmp",
            ncbi_division_file = "division.dmp",
            ncbi_citation_file = "citations.dmp"
        )
        Taxonomy.create_taxonomy_db(**params)
        self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 72).data, {'title': 'Unspecified'})
        self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 1).data, {'title': 'root'})
        
        
        Q = Taxonomy.search("methylotrophus")
        self.assertEqual(Q[0].title, "Methylophilus methylotrophus")