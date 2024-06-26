import os
import sys
import unittest

from gws_biota._helper.chebi import Chebi
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
            settings.get_variable("gws_biota:testdata_dir"),
            '../_helper/data/'
        )
        ontology = Chebi.create_ontology_from_file(testdata_path,'chebi_test.obo')
        list_chebi = Chebi.parse_onto_from_ontology(ontology)
        self.assertEqual(len(list_chebi), 18)
        self.assertEqual(list_chebi[2]['id'], 'CHEBI:24870')
        self.assertEqual(list_chebi[9]['id'], 'CHEBI:24060')