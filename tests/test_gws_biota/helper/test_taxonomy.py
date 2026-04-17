import os
import unittest

from gws_biota._helper.ncbi import Taxonomy as NCBITaxonomy
from gws_core import Settings

####################################################################################
#
#                                  TEST TAXONOMY PARSER
#
####################################################################################


class TestModel(unittest.TestCase):
    def test_db_object(self):
        settings = Settings.get_instance()
        testdata_path = os.path.join(
            settings.get_variable("gws_biota", "testdata_dir"), "../test_gws_biota/helper/data/"
        )

        dict_ncbi_names = NCBITaxonomy.get_ncbi_names(os.path.join(testdata_path, "names_test.dmp"))
        dict_taxons = NCBITaxonomy.get_all_taxonomy(
            dict_ncbi_names,
            os.path.join(testdata_path, "nodes_test.dmp"),
            os.path.join(testdata_path, "division.dmp"),
        )

        self.assertEqual(
            dict_taxons["72"],
            {"tax_id": "72", "ancestor": "71", "rank": "species", "division": "Bacteria"},
        )
        self.assertEqual(
            dict_taxons["1"],
            {
                "tax_id": "1",
                "name": "root",
                "ancestor": "1",
                "rank": "no rank",
                "division": "Unassigned",
            },
        )
