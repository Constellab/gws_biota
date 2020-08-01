import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings
from biota.db.protein import Protein

settings = Settings.retrieve()
test_data_path = settings.get_data("biota_test_data_dir")

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

        Protein.create_protein_db(test_data_path, **files_test)