import os
import unittest

from gws_biota._helper.brenda import Brenda
from gws_core import Settings

############################################################################################
#
#                                        Test Brenda class
#
############################################################################################


class TestBrenda(unittest.TestCase):
    def test_db_object(self):
        settings = Settings.get_instance()

        testdata_path = os.path.join(
            settings.get_variable("gws_biota", "testdata_dir"), "../test_gws_biota/helper/data/"
        )
        main_testdata_path = settings.get_variable("gws_biota", "testdata_dir")

        brenda = Brenda(
            brenda_file=os.path.join(testdata_path, "brenda_test.txt"),
            taxonomy_dir=main_testdata_path,
            bto_file=os.path.join(main_testdata_path, "bto_test.obo"),
            chebi_file=os.path.join(main_testdata_path, "chebi_test.obo"),
        )
        list_proteins, _ = brenda.parse_all_enzyme_to_dict()
        self.assertEqual(list_proteins[0]["organism"], "Pseudomonas sp.")
        self.assertEqual(list_proteins[6]["ec"], "1.13.11.38")
