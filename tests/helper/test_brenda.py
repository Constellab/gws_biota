import sys
import os
import unittest

from gws.settings import Settings
from gws.prism.controller import Controller
from biota.helper.brenda import Brenda

############################################################################################
#
#                                        Test Brenda class
#                                         
############################################################################################

class TestBrenda(unittest.TestCase):
    
    def test_db_object(self):
        settings = Settings.retrieve()
        test_data_path = settings.get_data("brenda_test_data_dir")
        brenda = Brenda(os.path.join(test_data_path, "brenda_test.txt"))
        list_proteins = brenda.parse_all_protein_to_dict()
    
        #print(list_proteins)

        self.assertEqual(list_proteins[0]['organism'], 'Pseudomonas sp.')
        self.assertEqual(list_proteins[6]['ec'], '1.13.11.38')