import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings

from biota.db.chebi_ontology import ChebiOntology

############################################################################################
#
#                                        TestChebiOntology
#                                         
############################################################################################
settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:chebi_testdata_dir")

class TestChebiOntology(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ChebiOntology.drop_table()
        ChebiOntology.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Compound.drop_table()
        pass

    def test_db_object(self):

        params = dict(
            biodata_dir = testdata_path,
            chebi_file = "chebi_test.obo",
        )
        
        ChebiOntology.create_chebi_ontology_db(**params)
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:24431').name, "chemical entity")
        self.assertEqual(ChebiOntology.get(ChebiOntology.chebi_id == 'CHEBI:17051').name, 'fluoride')
