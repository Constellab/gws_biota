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
            settings.get_variable("gws_biota", "testdata_dir"), "../_helper/data/"
        )
        base_biodata_dir = Settings.get_instance().get_variable("gws_biota", "biodata_dir")

        brenda = Brenda(
            brenda_file=os.path.join(testdata_path, "brenda_test.txt"),
            taxonomy_dir=os.path.join(base_biodata_dir, "ncbi", "taxdump"),
            bto_file=os.path.join(base_biodata_dir, "bto", "bto.owl"),
            chebi_file=os.path.join(base_biodata_dir, "chebi", "chebi.obo"),
        )
        list_proteins, _ = brenda.parse_all_enzyme_to_dict()
        self.assertEqual(list_proteins[0]["organism"], "Pseudomonas sp.")
        self.assertEqual(list_proteins[6]["ec"], "1.13.11.38")
