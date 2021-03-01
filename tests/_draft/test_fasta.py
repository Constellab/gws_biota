import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings
from biota.db.fasta import Fasta

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestGO(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        Fasta.drop_table()
        Fasta.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        Fasta.drop_table()
        pass
    
    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            fasta_file = "uniprot_sprot.fasta",
        )

        Fasta.create_fasta_db(**params)  

                