import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings
from biota.db.protein import Protein

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestProtein(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        Protein.drop_table()
        Protein.create_table()
   
    @classmethod
    def tearDownClass(cls):
        pass

    def test_db_object(self):
        files_test = dict(
            brenda_file = "brenda_test.txt"
        )

        Protein.create_protein_db(testdata_path, **files_test)