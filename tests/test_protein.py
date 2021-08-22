import sys
import os
import unittest

from gws_core import Settings, GTest
from gws_biota import Protein

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")

class TestGO(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        GTest.drop_tables()
        GTest.create_tables()
        
    @classmethod
    def tearDownClass(cls):
        GTest.drop_tables()
    
    def test_db_object(self):
        GTest.print("Protein")
        params = dict(
            biodata_dir = testdata_path,
            protein_file = "uniprot_sprot.fasta",
        )
        Protein.create_protein_db(**params)  

                