import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings
from biota.db.protein import Protein

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestGO(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        Protein.drop_table()
        Protein.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        Protein.drop_table()
        pass
    
    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            protein_file = "uniprot_sprot.fasta",
        )

        Protein.create_protein_db(**params)  

                