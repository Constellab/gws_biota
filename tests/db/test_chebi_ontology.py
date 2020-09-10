import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings

from biota.db.chebi_ontology import ChebiOntology

############################################################################################
#
#                                        TestChebiOntology
#                                         
############################################################################################
settings = Settings.retrieve()
testdata_path = os.path.join(
    settings.get_dir("biota:testdata_dir"),
    '../_helper/data/'
)

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
