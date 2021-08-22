import sys
import os
import unittest

from gws_core import Settings
from gws_biota._helper.brenda import Brenda

############################################################################################
#
#                                        Test Brenda class
#                                         
############################################################################################

class TestBrenda(unittest.TestCase):
    
    def test_db_object(self):
        settings = Settings.retrieve()
        testdata_path = os.path.join(settings.get_variable("gws_biota:testdata_dir"),'../_helper/data/')
        brenda = Brenda(os.path.join(testdata_path, "brenda_test.txt"))
        list_proteins, _ = brenda.parse_all_enzyme_to_dict()
        self.assertEqual(list_proteins[0]['organism'], 'Pseudomonas sp.')
        self.assertEqual(list_proteins[6]['ec'], '1.13.11.38')