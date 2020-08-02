import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings
from biota.db.enzyme import Enzyme
from biota.db.protein import Protein

settings = Settings.retrieve()
testdata_path = settings.get_data("biota:testdata_dir")

class TestEnzyme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Protein.drop_table()
        Enzyme.drop_table()
        Enzyme.create_table()
   
    @classmethod
    def tearDownClass(cls):
        pass

    def test_db_object(self):
        files_test = dict(
            brenda_file = "brenda_test.txt"
        )

        Enzyme.create_enzyme_db(testdata_path, **files_test)