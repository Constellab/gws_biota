import sys
import os
import unittest

from gws_core import Settings, GTest
from gws_biota import Taxonomy

############################################################################################
#
#                                        TestTaxonomy
#                                         
############################################################################################
settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")

class TestGO(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        GTest.drop_tables()
        GTest.create_tables()
        
    @classmethod
    def tearDownClass(cls):
        GTest.drop_tables()
    
    def test_db_object(self):
        GTest.print('Taxonomy')
        params = dict(
            biodata_dir = testdata_path,
            ncbi_node_file = "nodes_test.dmp",
            ncbi_name_file = "names_test.dmp",
            ncbi_division_file = "division.dmp",
            ncbi_citation_file = "citations.dmp"
        )
        Taxonomy.create_taxonomy_db(**params)
 
        self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 72).data, {'tax_id': '72', 'rank': 'species', 'division': 'Bacteria'})
        self.assertEqual(Taxonomy.get(Taxonomy.tax_id == 1).data, {'tax_id': '1', 'name': 'root', 'rank': 'no rank', 'division': 'Unassigned'})
        
        #Q = Taxonomy.select()
        #for t in Q:
        #    print(t.title)
        
        #Q = Taxonomy.search("methylotrophus")
        #self.assertEqual(Q[0].get_related().name, "Methylophilus methylotrophus")
        