import sys
import os
import unittest

from gws.settings import Settings
from biota._helper.chebi import Chebi



############################################################################################
#
#                                        Test Chebi class parser
#                                         
############################################################################################

class TestChebi(unittest.TestCase):
    
    def test_db_object(self):
        settings = Settings.retrieve()
        testdata_path = os.path.join(
            settings.get_dir("biota:testdata_dir"),
            '../_helper/data/'
        )

        # #### Test .csv/.tsv parser ####
        # list_comp = Chebi.parse_csv_from_file(testdata_path,'compounds_test.tsv')
        # self.assertEqual(len(list_comp), 18)
        # self.assertEqual(list_comp[0]['chebi_accession'], 'CHEBI:58321')
        # self.assertEqual(list_comp[8]['name'], 'S-adenosyl-L-methionine zwitterion')

        #### Test .obo parser ####
        ontology = Chebi.create_ontology_from_file(testdata_path,'chebi_test.obo')
        list_chebi = Chebi.parse_onto_from_ontology(ontology)

        self.assertEqual(len(list_chebi), 11)
        self.assertEqual(list_chebi[2]['id'], 'CHEBI:24870')
        self.assertEqual(list_chebi[9]['id'], 'CHEBI:24060')