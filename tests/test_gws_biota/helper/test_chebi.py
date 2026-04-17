import os
import unittest

from gws_biota._helper.chebi import Chebi
from gws_biota._helper.ontology import Onto
from gws_core import Settings

############################################################################################
#
#                                        Test Chebi class parser
#
############################################################################################


class TestChebi(unittest.TestCase):
    def test_db_object(self):
        settings = Settings.get_instance()
        testdata_path = os.path.join(
            settings.get_variable("gws_biota", "testdata_dir"), "../test_gws_biota/helper/data/"
        )
        corrected_path, corrected_file = Chebi.correction_of_chebi_file(testdata_path, "chebi_test.obo")
        ontology = Onto.create_ontology_from_file(corrected_path, corrected_file)
        list_chebi = Onto.parse_chebi_from_ontology(ontology)
        self.assertEqual(len(list_chebi), 18)
        self.assertEqual(list_chebi[2]["id"], "CHEBI:24870")
        self.assertEqual(list_chebi[9]["id"], "CHEBI:24060")
