import sys
import os
import unittest

from gws.settings import Settings
from gws.prism.controller import Controller
from biota._helper.brenda import Brenda

############################################################################################
#
#                                        Test Brenda class
#                                         
############################################################################################

class TestBrenda(unittest.TestCase):
    
    def test_db_object(self):
        settings = Settings.retrieve()
        testdata_path = settings.get_data("biota:brenda_testdata_dir")
        brenda = Brenda(os.path.join(testdata_path, "brenda_test.txt"))
        list_proteins = brenda.parse_all_protein_to_dict()
    
        self.assertEqual(list_proteins[0]['organism'], 'Pseudomonas sp.')
        self.assertEqual(list_proteins[6]['ec'], '1.13.11.38')